# Architecture

## Concise Product Vision

Dreamer2 is a durable companion system, not a themed chatbot skin. It combines a living shell, a replaceable behavior core, and an explicit continuity layer so identity can evolve visibly over time without sacrificing control.

The shell should be treated as a layered simulation on a character grid, not as a collection of hardcoded frame swaps. The source of truth is a scene model and render spec that can target multiple capability tiers without artistic collapse.

## Primary Layers

### Shell

Owns:

- terminal layout and regions
- capability detection and render-tier selection
- scene-model assembly for the visible shell
- portrait composition and ambient field rendering
- event distortion and redraw strategy
- transmission log presentation
- command entry and shell feedback
- panels, overlays, transitions, and cosmetic state

Does not own:

- language-model policy
- durable memory decisions
- tool execution logic

### Mind

Owns:

- conversation and task routing
- mode changes and mode policy
- provider/model adaptation
- tool/action orchestration
- extraction of memory candidates from events and outputs

Does not own:

- terminal rendering details
- long-term storage mechanics

### Memory

Owns:

- event storage
- durable memory curation
- artifact generation
- visible evolution state
- correction, prune, export, and inspection workflows

Does not own:

- model prompting strategy
- renderer-specific behavior

## Shared Boundary

`layers/shared` holds canonical IDs, event envelopes, seeded randomness rules, time handling, and cross-layer schemas. Shared code may normalize data, but it must not become a hidden fourth application layer.

## Capability-Aware Rendering Strategy

The shell must scale across environments through explicit capability tiers:

- `pure-text`: character cells plus ANSI styling only; expected to work almost everywhere
- `rich-unicode`: wider glyph families, denser character choices, and richer color support when available
- `hybrid-graphics`: optional cinematic moments or image-like overlays for advanced graphics protocols or richer web/canvas terminal surfaces

The highest tier may enrich the experience, but it may never define the product's identity by itself. The lowest tier must still feel intentional, premium, and unmistakably the same companion.

## Runtime Flow

1. Shell emits a `session_event` from user input, mode change, or shell lifecycle.
2. Mind receives the event, resolves command routing, conversation behavior, and optional tool/action execution.
3. Mind emits outputs:
   - transmission lines
   - mode transitions
   - memory candidates
   - state hints for portrait and panels
4. Memory stores raw history, promotes or rejects candidate memories, updates artifacts/evolution state, and returns visible continuity deltas.
5. Shell resolves the active capability tier and builds a scene model from current mode, visible artifacts, active portrait parts, and ambient-field rules.
6. Shell advances deterministic randomness streams, ambient simulation, portrait micro-motion, mode overlays, and active event distortions.
7. Shell composites the layered scene into a character grid or render buffer.
8. Shell computes a diff against the previous frame and redraws only changed cells or changed regions where possible.

## Frame Pipeline

The conceptual frame loop should remain stable even if the implementation surface changes:

1. evaluate current mode, state, and shell activity
2. advance deterministic randomness streams
3. update ambient field simulation
4. update portrait micro-motion and slot-state behavior
5. apply mode overlays
6. apply event distortions if active
7. composite to character grid or render buffer
8. diff against prior frame
9. redraw only changed cells or regions where possible

This is an abstraction boundary, not a mandate for a fixed game loop or library choice.

## Scene And Layer Model

The shell scene should be composed from at least these conceptual layers:

- `core silhouette`: the stable iconic portrait
- `ambient field`: sparse drifting signal and environmental life
- `state`: mode-driven visual behavior and overlays
- `event`: rare high-impact transitions, unlocks, strain, and dream distortions
- `text-ui`: prompts, logs, status, panels, and information surfaces

The text and command surface always wins readability conflicts. Calm and clarity outrank spectacle.

## Replaceable Interface Boundaries

- shell renderer
- capability detector
- scene model builder
- portrait compositor
- glyph-language registry
- animation scheduler
- ambient field engine
- event distortion engine
- render diff engine
- command router
- session manager
- mode manager
- memory manager
- artifact manager
- memory-to-symbol mapper
- module loader
- optional hybrid graphics adapter
- model/provider adapter
- tool/action bridge
- persistence adapter
- import/export adapter

Detailed interface contracts live in `specs/INTERFACES.md`.

## Recommended Abstraction Choices

These are boundaries worth protecting even if the eventual implementation stack changes:

- Use manifest-driven packs rather than hardcoded part registration.
- Use a scene model and canonical render-state contract between `Mind`/`Memory` outputs and `Shell`.
- Separate raw event history from curated durable memory.
- Treat glyph families as semantic material, not generic characters.
- Keep procedural motion deterministic where identity matters and random only within declared budgets.
- Preserve a diff-oriented redraw boundary so the implementation can stay efficient on constrained terminals.
- Route external models/providers through a provider adapter boundary.
- Route tool execution through an action bridge boundary with auditable events.

## Optional Implementation Topology

One pragmatic starting point is:

- one process for `Shell`
- one local service or in-process module for `Mind`
- one local file-backed or lightweight database adapter for `Memory`

That topology is optional. The architecture should survive a later move to multi-process, local-first, or hybrid local/remote execution.
