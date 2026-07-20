"""
Turns a natural language command into a valid scene spec.
Process: command -> prompt -> LLM -> parse JSON -> validate -> (repair/retry if needed) -> spec
"""
import re
import json
from validator import validate_spec
from primitive_vocabulary import VALID_TYPES, VALID_COLORS

GENERATION_PROMPT = """You are generating a 2D grid-world environment as JSON.

TASK: {command}

OUTPUT: a single JSON object no prose, no markdown fences. Use the following Schema:
{{
"grid_size": <int, 6-12>,
"mission": "<short description of the objective>",
"agent_spawn": {{"pos": [x, y], "dir": <0=east,1=south,2=west,3=north>}},
"objects": [{{"type": "<type>", "pos": [x, y], "color": "<color>"}}],
"objective" {{"type": "<reach_goal|pickup|reach_avoiding|sequence>", "color": "<color, only if the objective involves a specific item>"}}
}}

RULES (required):
- The outer border is automatically walls. Objects should only be placed on INTERIOR cells:
x and y must be between 1 and grid_size-2 inclusive.
- Valid types: {types}. Only key/ball/box/door take a "color".
- Valid colors: {colors}
- Exactly ONE object of type "goal".
- No two objects on the same cell, the agent must not spawn on an object.
- The goal must be reachable from the spawn (do not fully wall it off)
- Set "objective" to match the task:
  - just reach a goal = {{"type": "reach_goal"}}
  - pick up a specific item = {{"type": "pickup", "color": "<item color>"}}
  - reach a goal while avoiding lava = {{"type": "reach_avoiding"}}
  - pick up an item AND then reach the goal = {{"type": "sequence", "color": "<item color>"}}
  - "objective" is ALWAYS a JSON object with a "type" field.
Return only the JSON object."""

REPAIR_PROMPT = """The JSON you produced was invalid. Errors include:
{errors}

What was produced by you:
{previous}

Fix ALL listed errors. If the goal is "not reachable", you have placed too many walls and sealed it off. 
You must remove several walls to open a clear, connected path from the agents spawn to the goal. Prefer fewer walls over a dense maze.
Return a corrected single JSON object that fixes all listed errors. No prose, no markdown fences."""

def _parse(output: str) -> dict:
    # Extracting a JSON object from the model's text
    output = output.strip()
    if "```" in output:
        parts = output.split("```")
        output = max(parts, key=len)
        if output.startswith("json"):
            output = output[4:]
        output = output.strip()
    # Extract JSON object even if surronded by prose
    match = re.search(r"\{.*\}", output, re.DOTALL)
    if match:
        output = match.group(0)
    return json.loads(output)

def generate_spec(command: str, client, max_repairs: int = 3):
    # Returns (spec, log). Raises if it can't produce a valid spec in time.
    log = []
    prompt = GENERATION_PROMPT.format(
        command = command, types = VALID_TYPES, colors = VALID_COLORS
    )
    # Make the LLM call on the prompt
    output = client.complete(prompt)

    for attempt in range(max_repairs + 1):
        try:
            spec = _parse(output)
            parse_error = None
        except (json.JSONDecodeError, IndexError) as e:
            spec, parse_error = None, f"not valid JSON: {e}"

        # If JSON is invalid errors [] just becomes parse_error otherwise we validate the spec
        errors = [parse_error] if parse_error else validate_spec(spec)
        log.append({"attempt": attempt, "output": output, "errors": errors})

        if not errors:
            return spec, log
        
        # Repairing
        output = client.complete(REPAIR_PROMPT.format(
            errors = "\n".join(f"- {e}" for e in errors),
            previous = output
        ))

    raise RuntimeError(f"failed to generate valid spec after {max_repairs} repairs. Log: {log}")