"""End-to-end generation"""
import sys
from client import GeminiClient
from generator import generate_spec
from engine import SpecEnv
from verifier import Verifier
from navigator import plan_navigation, navigate
from dotenv import load_dotenv
from client import AnthropicClient

load_dotenv()  
# If were not given a text prompt default to the following
command = sys.argv[1] if len(sys.argv) > 1 else "A room with a key, a locked door, and a goal behind it"

client = AnthropicClient()

# Generation
spec, log = generate_spec(command, client)
print(f"Command: {command}")
print(f"Attempts: {len(log)}")
for entry in log:
    print(f" attempt {entry['attempt']}: errors = {entry['errors']}")
print(f"Spec: {spec}\n")

# Build, navigate, verify
plan_env = SpecEnv(spec) # Use a non render env for planning
plan = plan_navigation(plan_env, spec, client)
print(f"Plan: {plan}")

print("Opening visual representation...\n")
env = SpecEnv(spec, render_mode="human") # Now we swap to a render inclusive env 
verifier = Verifier(spec)
success, trace = navigate(env, plan, verifier, render=True, delay=0.5, start_pause=3)

print("\nSteps:")
for s in trace["steps"]:
    print(" ", s)
print(f"\nSuccess: {success}")
input("\nPress Enter to close the visual")