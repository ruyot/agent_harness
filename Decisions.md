# Design Decisions

This document records key design decisions behind the harness including the reasoning behind them and the trade-offs accepted.

## Backend-agnostic scene spec as the core interface
The generator creates a **scene spec** (plain JSON data). An **adapter** (engine) translates. The spec never references engine specifics. 

- Why: By keeping the environment specification separate from the engine it makes it so that a future 3D engine (i.e. MiniWorld) is more easy to integrate. 

## Generator is deliberately unaware of the target engine
The generation prompt describes the abstract grid world in its own vocabulary, it never mentions MiniGrid.

- Why: Leaking the backend into the generator could easily bias output toward engine-specific assumptions and give unnecessary information to the model without challenging it freely.

## Reliability lives in the harness, not just the prompt

There are two layers of defense against invalid environments:
- Prompt layer: The generation prompt front-loads constraints (bounds, one goal, valid, colors, reachability)
- System layer: A validator catches malformed/contradictory specs and returns a list of descriptive errors, which are fed back to the model for repair and retry.

- Why: The model can ignore or miss prompt instructions, but the validator acts as a guarantee. This helps especially with smaller models that may miss on their first try or create a small error. This can then be caught and resent to the model for a retry.

- Trade-off: Extra model calls do occur on repair, but a max of 3 model calls (3 continuous fails) is set.

## Validator returns a list of errors, not a boolean

- Why: The full error list becomes the repair feedback, letting the model fix its mistakes.

## Model access behind an `LLMClient` interface

An abstract `LLMClient` with a single `complete(prompt) -> str` method. 

- Why: Makes the harness model-agnostic, and lets any provider be swapped with only a few lines. A stateful backend such as Claude Code can also be added later.

## Navigator consumes a rendered observation, never the spec

The navigator is fed a rendered text view of the grid and not the spec directly.

- Why: this mirrors a vision policy, which sees frames instead of structured data. The model also spends its capacity on planning and coming up with a navigation strategy rather than reconstructing geometry from a coordinate list.

## Full-observability
The navigator is shown the whole grid and is asked for a complete action sequence which is executed in one pass.

- Why: Full-observability is a clean and effective way of building the closed loop while avoiding the tracing of explicit memory as would be needed with partial observability. Partial observability is more of a future add on.

- Trade-offs: one-shot plans can commit to a route that walks into a wall, but this allows for the testing of both agent failures and successes with the freedom to fail. 

Model capability does not also linearly predict navigation success, a smaller model can sometimes navigate simpler grids more reliably than a larger one, since the task rewards a solution that isn't over analyzed.

## Verification reads engine state, not the action sequence
The verifier judges success from ground-truth engine state (`agent_pos`, `carrying`, cell contents) against the spec's declared `objective`. It never checks the action list.

- Why: The engine already enforces action legality during execution (can't open locked doors without the key or lava ends the navigation). This is why outcomes are verified instead of steps, they're simpler and more robust. 

## Declared, typed objectives

Objectives are declared in the spec and typed: `reach_goal`, `pickup`, `reach_avoiding`, `sequence`. Trajectory-dependent ones (e.g. avoidance) are tracked step-by-step via `observe()`. Final objectives are read from end state via `check()`.

- Why: Makes environments evaluable. Success is a declared, checkable condition, not just "reached goal." This is what lets the harness serve as a training/eval mechanism.

- Trade-off: `sequence` is not true temporal ordering yet.

## Reachability is guaranteed, not requested

The validator runs a flood-fill from the spawn and rejects any spec where the goal is walled off. Unsolvable specs go back through the repair loop until solvable.

- Why: Models can't reliably reason about global connectivity while placing walls, so they sometimes seal off the goal despite being told not to. A flood-fill guarantees solvability and allows for model redirection after error notification.