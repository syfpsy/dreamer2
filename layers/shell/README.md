# Shell Layer

Owns the visible companion surface.

Responsibilities:

- terminal layout and composition
- portrait rendering
- ambient field behavior
- overlays, panels, and transmission presentation
- command capture and shell feedback

Inputs:

- render state
- mode state
- visible artifacts
- shell config and theme data

Outputs:

- user command events
- focus and layout events
- shell lifecycle events

The shell should remain renderer-swappable. It consumes a render spec; it does not invent core behavior.
