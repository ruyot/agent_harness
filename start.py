"""End-to-end generation"""
import sys
from client import GeminiClient
from generator import generate_spec
from engine import SpecEnv
from verifier import Verifier
from navigator import navigate

# If were not given a text prompt default to the following
command = sys.argv[1] if len(sys.argv) > 1 else "A room with a key, a locked door, and a goal behind it"

client = GeminiClient()

# Generation
spec, log = generate_spec(command, client)
print(f"Command: {command}")
print(f"Attempts: {len(log)}")
for entry in log:
    print(f" attempt {entry['attempt']}: errors = {entry['errors']}")
print(f"Spec: {spec}\n")

# Build, navigate, verify
env = SpecEnv(spec)
verifier = Verifier(spec)
success, trace = navigate(env, spec, client, verifier)

print(f"Plan: {trace['plan']}")
print("Steps:")
for s in trace["steps"]:
    print(" ", s)
print(f"]nSuccess: {success}")