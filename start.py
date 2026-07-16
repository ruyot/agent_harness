"""End-to-end generation"""
import sys
from client import GeminiClient
from generator import generate_spec
from engine import SpecEnv
from minigrid.manual_control import ManualControl

# If were not given a text prompt default to the following
command = sys.argv[1] if len(sys.argv) > 1 else "A room with a key, a locked door, and a goal behind it"

client = GeminiClient()
spec, log = generate_spec(command, client)

print(f"Command: {command}")
print(f"Attempts: {len(log)}")

for entry in log:
    print(f" attempt {entry['attempt']}: errors = {entry['errors']}")
print(f"Spec: {spec}\n")

env = SpecEnv(spec, render_mode = "human")
env.reset()
ManualControl(env, seed=42).start()