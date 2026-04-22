# Specs

This folder is the contract surface for the project.

- `INTERFACES.md`: implementation-neutral runtime boundaries.
- `schemas/`: JSON schemas for configs, packs, memory records, commands, modes, scene/render state, procedural behaviors, and session events.
- `examples/`: starter payloads that future implementations can load and validate.

The intent is simple: content and behavior should survive a renderer swap, provider swap, or persistence swap.
