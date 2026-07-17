"""
Checks if a scene spec is legal before it reaches the engine.
Bad specs can be caught and repaired rather than crashing and producing broken environments.
"""
from primitive_vocabulary import PRIMITIVES, VALID_COLORS, VALID_TYPES

def validate_spec(spec: dict) -> list[str]:
    """Returns a list of error strings. Empty list == valid spec."""
    errors = []

    # Top level required fields
    for field in ["grid_size", "mission", "agent_spawn", "objects"]:
        if field not in spec:
            errors.append(f"missing top-level field: '{field}'")
    if errors:
        return errors 
    
    size = spec["grid_size"]
    playable = range(1, size - 1) # Playable cells (since the border is walled)


    def in_bounds(pos):
        return len(pos) == 2 and pos[0] in playable and pos[1] in playable
    
    # Agent Spawn
    spawn = spec["agent_spawn"]
    if not in_bounds(spawn.get("pos", [])):
        errors.append(f"agent_spawn pos {spawn.get('pos')} out of interior bounds")
    if spawn.get("dir") not in (0, 1, 2, 3):
        errors.append(f"agent_spawn dir must be 0-3, got {spawn.get('dir')}")
    
    # Objects
    occupied = {}
    has_goal = False
    
    for i, obj in enumerate(spec["objects"]):
        t = obj.get("type")
        # Check if the type associated to the object is valid
        if t not in VALID_TYPES:
            errors.append(f"object {i} has unknown type '{t}'")
            continue
        # Check if the objects required fields relative to its type are added
        for req in PRIMITIVES[t]["requires"]:
            if req not in obj:
                errors.append(f"object {i} with type ({t}) is missing required field '{req}'")
        if PRIMITIVES[t]["color"] and obj.get("color") not in VALID_COLORS:
            errors.append(f"object {i} with type ({t}) contains invalid color '{obj.get('color')}'")
        if "pos" in obj and not in_bounds(obj["pos"]):
            errors.append(f"object {i} with type ({t}) contains invalid position {obj['pos']} out of interior bounds")

        # Check if objects overlap
        if "pos" in obj:
            key = tuple(obj["pos"])
            if key in occupied:
                errors.append(f"object {i} with type ({t}) at position {key} is already used by {occupied[key]}")
            occupied[key] = t
        if t == "goal":
            has_goal = True

        # Agent spawn cant be on an object
    if tuple(spawn.get("pos", [])) in occupied:
        errors.append(f"agent spawns on {occupied[tuple(spawn['pos'])]}")

    if not has_goal:
        errors.append("spec has no goal object")

    # Check objective
    VALID_OBJECTIVES = {"reach_goal", "pickup", "reach_avoiding", "sequence"}
    obj = spec.get("objective")
    if obj is None:
        errors.append("missing 'objective' field")
    elif obj.get("type") not in VALID_OBJECTIVES:
        errors.append(f"objective type must be one of {VALID_OBJECTIVES}, got {obj.get('type')}")
    elif obj["type"] in ("pickup", "sequence") and obj.get("color") not in VALID_COLORS:
        errors.append(f"objective '{obj['type']}' requires a valid color, got {obj.get('color')}")

    return errors