"""
Judges whether the navigation satisfied the spec's objective, checked against the final
engine state. Mirrors the validator for environment generation.
"""
from minigrid.core.world_object import Goal

class Verifier:
    def __init__(self, spec: dict):
        self.objective = spec.get("objective", {"type": "reach_goal"})
        self.touched_lava = False

    def observe(self, env):
        # If the agent touches lava at any point its recorded and persists
        cell = env.grid.get(*env.agent_pos)
        if cell is not None and cell.type == "lava":
            self.touched_lava = True

    def check(self, env) -> bool:
        # Final verdict from engine state
        t = self.objective["type"]

        if t == "reach_goal":
            return self._at_goal(env)

        if t == "pickup":
            held = env.carrying
            want = self.objective.get("color")
            return held is not None and (want is None or held.color == want)

        if t == "reach_avoiding":
            return self._at_goal(env) and not self.touched_lava

        if t == "sequence":
            # e.g. must be holding the target AND standing on goal
            held = env.carrying
            want = self.objective.get("color")
            # If the agent is holding something and there is either no color associated to the object or the associated color equals to what the object colour should be
            holding_ok = held is not None and (want is None or held.color == want)
            return holding_ok and self._at_goal(env)

        return False
    
    # Dont need self
    @staticmethod
    def _at_goal(env) -> bool:
        cell = env.grid.get(*env.agent_pos)
        return isinstance(cell, Goal)