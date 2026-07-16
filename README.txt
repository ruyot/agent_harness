# Infinite Environment Generation using an Agent Harness

## Overview
This project is a model agnostic, agent harness that lets 
a language model generate 2d environments from natural-language
commands and navigate the environments it produces to accomplish objectives.

Environments are expressed as **scene specifications** (plain data), which an adapter translates 
into a runnable [MiniGrid](https://minigrid.farama.org/) environemnt. Minigrid is a 2d MiniGrid
world that consists of walls, lava, keys, locked doors, and goals. Because the spec is seperate from the engine, 
the same generation and navigation pipeline can target other backends (e.g. a 3D MiniWorld adapter) by swapping only the adapter.

The agent operates under **partial observabilty** (It sees a local view, not the entire grid), which tests interpretation, 
inference, and exploration rather than static reading while mirroring the conditions that a vision-based policy would face.
