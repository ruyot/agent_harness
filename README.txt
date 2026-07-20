# Infinite Environment Generation using an Agent Harness

## Overview
This project is a model agnostic, agent harness that lets 
a language model generate 2d environments from natural-language
commands and navigate the environments it produces to accomplish objectives.

Environments are expressed as **scene specifications** (plain data), which an adapter translates 
into a runnable [MiniGrid](https://minigrid.farama.org/) environment. Minigrid is a 2d grid
world that consists of walls, lava, keys, locked doors, and goals. Because the spec is separate from the engine, 
the same generation and navigation pipeline can target other backends (e.g. a 3D MiniWorld adapter) by swapping only the adapter.

![Multi Door Environment: the model designs and solves a multi door maze](path)

*Prompt: Create a maze with multiple doors, within the maze there should be multiple keys of matching colour to the doors, in order for the agent to reach the goal they must use the keys to go through subsequent doors and reach the goal.*

## Quick start
```bash
pip install -r requirements.txt

# set an API key (.env file or environment variable, example env also given)
echo "ANTHROPIC_API_KEY=your_key_here" > .env

python start.py "a room with a key, a locked door, and a goal behind it."
```

You'll see generation attempts in the terminal along with the resulting spec, agent's plan, and a window that renders animating the agent traversing the environment.
The step by step trace and final success (true/false) are also included. Pressing enter in the terminal exits a render alongside quitting pygame.

## Example commands
```bash
python start.py "a twisting maze with a goal at the end"
python start.py "reach the goal while avoiding a patch of lava"
python start.py "a room where the agent must pick up the red key"
python start.py "make something difficult"
python start.py "create a maze with multiple coloured keys and matching doors that must be opened in sequence to reach the goal"
```

# Choosing models
The harness is provider-agnostic behind a small `LLMClient` interface. 
It currently works with Anthropic and Gemini backends and uses Fable 5 from Anthropic as a default.
To use Gemini instead, change one line in start.py:

```python
client = GeminiClient()
```
and set `GEMINI_API_KEY`

# More Demos

## Architecture
The pipeline for the harness is split into phases, each in its own group:

**Environment**
- `generator.py` - command → prompt → LLM → parsed spec → validate → repair loop
- `environment_validation.py` - structural checks + a flood-fill reachability check
- `engine.py` - a `SpecEnv` adapter that builds a MiniGrid environment from a spec
- `primitive_vocabulary.py` - the single source of truth for valid object types,
  colours, and required fields (read by both the validator and the adapter)

**Navigation**
- `navigator.py` - renders the environment for the model, gets an action plan,
  executes it against the engine
- `navigation_validation.py` - verifies the declared objective from engine state

**Shared**
- `client.py` - the `LLMClient` interface and its backends (Anthropic, Gemini,
  plus a scripted `TestingClient` for deterministic, no-API testing)
- `start.py` - end-to-end orchestration

The generator emits plain data and doesn't reference the engine. Only the adapter (`engine.py`) knows the engine,
so retargeting to a different backend (e.g. a 3D engine) is a new adapter not a codebase rewrite.

For a more in-depth discussion on design decisions, conclusions, and outcomes see [`DECISIONS.md`](DECISIONS.md).

## Limitations & observations
- Full observability: The agent plans the whole action list up front with no execution feedback, so it can commit to a plan that walks into a wall.
Although the harness combats this through the use of retrying and redirecting the agent using its output, the next step would be partiall-observable navigation which is step-wise.

# References
- MiniGrid / MiniWorld (Farama) - the 2D engine used, and its 3D sibling that
  the adapter design points toward.
- BabyAI - mission-conditioned gridworld task families, a reference for the
  objective-difficulty ladder

