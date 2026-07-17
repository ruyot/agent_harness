"""
Drives an agnet through an environment specification to satify the spec's delcared objective ie "reach the goal".
For a first pass, full observability is implemented.
"""
import json
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
    # Rendering the full grid as text for the model (full observability).
    grid = env.grid
    lines = []
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
                row.append(cell.type[0].upper())  # W(all), K(ey), D(oor), G(oal), L(ava)...
        lines.append("".join(row))
    facing = DIR_NAMES[env.agent_dir]
    return f"Agent 'A' faces {facing}.\n" + "\n".join(lines)

PLAN_PROMPT = """You are controlling an agent in a 2D grid. Legend:
A=the agent  .=floor (empty)  W=wall  G=goal  K=key  D=door  L=lava  B=ball  X=box

{grid}

Movement is egocentric (relative to the way you face):
- "forward" moves one cell in your facing direction
- "left"/"right" turn you (they do not move you)
- "pickup" picks up the item in the cell you face
- "toggle" opens a door in the cell you face (needs the matching key in hand)

OBJECTIVE: {mission}

Return a JSON list of actions to accomplish the objective, e.g.
["forward","forward","left","forward","pickup"]
Return ONLY the JSON list."""


# Parsing the JSON list
def _parse_actions(output: str) -> list[str]:
    output = output.strip()
    if output.startswith("```"):
        output = output.split("```")[1]
        if output.startswith("json"):
            output = output[4:]
    return json.loads(output)

# Navigation
def navigate(env, spec, client, verifier):
    # Execution and verification, Returns (success, trace).
    env.reset()
    prompt = PLAN_PROMPT.format(grid=describe_full(env), mission=spec["mission"])

    plan = _parse_actions(client.complete(prompt))
    trace = {"plan": plan, "steps": [], "success": False}

    for name in plan:
        if name not in ACTION_MAP:
            trace["steps"].append({"action": name, "error": "unknown action"})
            continue
        # Only need terminated and truncated observability we check ourselves in the verifier
        _, _, terminated, truncated, _ = env.step(ACTION_MAP[name])
        verifier.observe(env)
        trace["steps"].append({
            "action": name,
            "agent_pos": tuple(env.agent_pos),
            "terminated": terminated, "truncated": truncated,
        })
        if terminated or truncated:
            break
    
    trace["success"] = verifier.check(env)
    return trace["success"], trace