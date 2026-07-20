"""
Drives an agent through an environment specification to satisfy the spec's delcared objective ie "reach the goal".
For a first pass, full observability is implemented.
"""
import re
import json
import time
from minigrid.core.actions import Actions

# Mapping text to valid MiniGrid actions
ACTION_MAP = {
    "left": Actions.left,       # turn left
    "right": Actions.right,     # turn right
    "forward": Actions.forward,
    "pickup": Actions.pickup,
    "drop": Actions.drop,
    "toggle": Actions.toggle,   # open doors etc
    "done": Actions.done,
}

DIR_NAMES = {0: "east", 1: "south", 2 : "west", 3 : "north"}

def describe_full(env) -> str:
    # Rendering the full grid as text for the model (full observability)
    grid = env.grid
    lines = []
    objects = []

    for y in range(grid.height):
        row = []
        for x in range(grid.width):
            if (x, y) == tuple(env.agent_pos):
                row.append("A")  # agent
                continue
            cell = grid.get(x, y)
            if cell is None:
                row.append(".")
            else:
                row.append(cell.type[0].upper())  # W(all), K(ey), D(oor), G(oal), L(ava)
                if cell.type != "wall":
                    color = getattr(cell, "color", "")
                    label = f"{color} {cell.type}".strip()
                    objects.append(f"{label} at ({x}, {y})")
        lines.append(f"{y:2} " + "".join(row))

    # Header
    width = grid.width
    header = "   " + "".join(str(x % 10) for x in range(width))

    facing = DIR_NAMES[env.agent_dir]
    pos = tuple(int(c) for c in env.agent_pos)
    obj_block = "\n".join(f"- {o}" for o in objects) if objects else "- (none)"

    return (
        f"Agent 'A' is at position {pos} and faces {facing}.\n\n"
        f"Objects (type, colour, position):\n{obj_block}\n\n"
        f"Grid (x = column across the top, y = row down the left side):\n"
        f"{header}\n"
        + "\n".join(lines)
    )

PLAN_PROMPT = """You are controlling an agent in a 2D grid. Legend:
A=the agent  .=floor (empty)  W=wall  G=goal  K=key  D=door  L=lava  B=ball  X=box

{grid}

Movement is egocentric (relative to the way you face):
- "forward" moves one cell in your facing direction
- "left"/"right" turn you (they do not move you)
- "pickup" picks up the item in the cell you face
- "drop" places the item you carry into the empty cell in front of you
- "toggle" interacts with the object in front of you: opens/unlocks a door (needs the matching-color key in hand), or opens a box

OBJECTIVE: {mission}

Return a JSON list of actions to accomplish the objective, e.g.
["forward","forward","left","forward","pickup"]

Do NOT explain your reasoning. Do NOT show your work. Output ONLY the JSON list
of actions on a single line, nothing before and nothing after"""


# Parsing the JSON list
def _parse_actions(output: str) -> list[str]:
    # Extracting a JSON object from the model's text
    output = output.strip()
    if "```" in output:
        parts = output.split("```")
        output = max(parts, key=len)
        if output.startswith("json"):
            output = output[4:]
        output = output.strip()
    # Extract JSON array even if surronded by prose, take the last one
    matches = re.findall(r"\[[^\[\]]*\]", output, re.DOTALL)
    if matches:
        output = matches[-1]
    return json.loads(output)

# Generate the full action list from the environment view
def plan_navigation(env, spec, client):
    env.reset()
    prompt = PLAN_PROMPT.format(grid=describe_full(env), mission=spec["mission"])
    plan = _parse_actions(client.complete(prompt))
    return plan

 # Execution and verification, run the plan against the engine
def navigate(env, plan, verifier, render=False, delay=0.4, start_pause=0):
    env.reset()
    trace = {"plan": plan, "steps": [], "success": False}
    
    if render:
        env.render()
        time.sleep(start_pause)

    for name in plan:
        if name not in ACTION_MAP:
            trace["steps"].append({"action": name, "error": "unknown action"})
            continue
        # Only need terminated and truncated observability we check ourselves in the verifier
        _, _, terminated, truncated, _ = env.step(ACTION_MAP[name])
        verifier.observe(env)

        if render:
            env.render()
            time.sleep(delay)

        trace["steps"].append({
            "action": name,
            "agent_pos": tuple(env.agent_pos),
            "terminated": terminated, "truncated": truncated,
        })
        if terminated or truncated:
            break
    
    trace["success"] = verifier.check(env)
    return trace["success"], trace