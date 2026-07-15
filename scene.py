from engine import SpecEnv

spec = {
    "grid_size": 8,
    "mission": "reach the green goal",
    "max_steps": 256,
    "agent_spawn": {"pos": [1,1], "dir": 0},
    "objects": [
        {"type": "goal", "pos": [6, 6]},
        {"type": "wall", "pos": [1,4]}
    ]
}

# dir 0 is east
# the border isnt counted so a grid size of 8 is actually a 6x6 grid

env = SpecEnv(spec, render_mode = "human")
env.reset()

from minigrid.manual_control import ManualControl
ManualControl(env, seed=42).start()