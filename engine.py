
from minigrid.minigrid_env import MiniGridEnv
from minigrid.core.grid import Grid
from minigrid.core.mission import MissionSpace
from minigrid.core.world_object import Wall, Lava, Key, Door, Ball, Box, Goal

class SpecEnv(MiniGridEnv):
    """Minigrid environment constructed from a scene spec"""

    def __init__(self, spec: dict, **kwargs):
        self.spec = spec # storing spec so we can use it later
        
        # Mission comes from the spec (originates from the users text command)
        # Since the spec is a dictionary we can use mission as a key and get the user input (task string)
        mission = spec["mission"]
        # Minigrid needs a function for the mission, but we only need the string so we pass a function with no params and return the string
        mission_space = MissionSpace(mission_func=lambda: mission) 


        size = spec["grid_size"] # pull the grid size from the spec
        max_steps = spec.get("max_steps", 4 * size**2)

        super().__init__(
            mission_space = mission_space,
            grid_size = size,
            max_steps = max_steps,
            see_through_walls = False, # Partial observability
            **kwargs,
        )

    def _gen_grid(self, width, height):
        self.grid = Grid(width, height)
        self.grid.wall_rect(0, 0, width, height)

        for obj in self.spec["objects"]:
            x, y = obj["pos"]
            t = obj["type"]
            if t == "wall":
                self.grid.set(x, y, Wall())
            elif t == "lava":
                self.grid.set(x, y, Lava())
            elif t == "key":
                self.grid.set(x, y, Key(obj["color"]))
            elif t == "door":
                self.grid.set(x, y, Door(obj["color"], is_locked=obj.get("locked", False)))
            elif t == "ball":
                self.grid.set(x, y, Ball(obj["color"]))
            elif t == "box":
                self.grid.set(x, y, Box(obj["color"]))
            elif t == "goal":
                self.put_obj(Goal(), x, y)

        spawn = self.spec["agent_spawn"]
        self.agent_pos = tuple(spawn["pos"])
        self.agent_dir = spawn["dir"]
        self.mission = self.spec["mission"]
