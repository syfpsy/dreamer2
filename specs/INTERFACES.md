# Interface Contracts

These interfaces are conceptual boundaries. The eventual implementation language can express them differently, but the responsibilities should remain stable.

## Shell Renderer

Purpose:

- turn validated scene and render state into terminal output or a richer shell surface

Consumes:

- capability tier
- scene model
- theme
- portrait composition
- panel state
- transmission log
- ambient field state

Produces:

- rendered frame
- shell interaction events

## Capability Detector

Purpose:

- inspect the current shell environment and select a supported render tier

Consumes:

- terminal metadata
- color depth
- Unicode support assumptions
- graphics protocol availability
- performance budget hints

Produces:

- capability tier
- supported feature flags
- renderer constraints

## Scene Model Builder

Purpose:

- assemble the canonical shell scene from mode, artifacts, portrait state, ambient rules, and events

Consumes:

- mode state
- artifact deltas
- loaded packs
- shell config
- seeded randomness streams

Produces:

- scene model
- layer ordering
- motion and glitch budgets

## Portrait Compositor

Purpose:

- combine slot parts, overlays, artifacts, and mode effects into a composed portrait frame

Consumes:

- active part IDs
- pack registry
- glyph-family rules
- theme palette
- mode behavior
- artifact overlays
- seeded randomness state

Produces:

- portrait layer stack
- final portrait frame

## Glyph-Language Registry

Purpose:

- define semantic glyph families and substitution constraints per capability tier

Consumes:

- theme and profile data
- glyph-family manifests
- capability tier

Produces:

- family lookup tables
- substitution constraints
- per-region glyph budgets

## Animation Scheduler

Purpose:

- advance micro-motion and event motion on deterministic cadences

Consumes:

- mode profile
- part animation personalities
- ambient field rules
- current clock

Produces:

- next animation tick state

## Ambient Field Engine

Purpose:

- simulate low-energy shell life in negative space and around portrait edges

Consumes:

- ambient behavior manifests
- mode state
- seeded randomness streams
- region rules

Produces:

- ambient cell updates
- active companion motion lanes
- field event hints

## Event Distortion Engine

Purpose:

- apply rare readable distortions for wake, dream, unlock, strain, or memory resurfacing events

Consumes:

- event queue
- distortion preset registry
- capability tier
- glitch budget

Produces:

- event layer mutations
- transmission resolution effects
- temporary render overrides

## Render Diff Engine

Purpose:

- compare the new frame against the previous frame and minimize redraw cost

Consumes:

- previous composed frame
- next composed frame
- renderer constraints

Produces:

- changed cells
- changed regions
- redraw plan

## Command Router

Purpose:

- resolve shell input into command handlers, directives, or send-through transmissions

Consumes:

- command registries
- loaded modules
- current mode
- shell input

Produces:

- command execution request
- validation errors
- help payloads

## Session Manager

Purpose:

- maintain current session lifecycle, transcript, and immediate context window

Consumes:

- shell events
- mind outputs

Produces:

- session records
- active session context

## Mode Manager

Purpose:

- own explicit and inferred mode state

Consumes:

- shell hints
- command outcomes
- tool pressure
- system strain or recovery signals

Produces:

- active mode
- transition reason
- shell and memory policy hints

## Memory Manager

Purpose:

- score, promote, revise, and retire durable memory

Consumes:

- raw events
- memory candidates
- promotion rules
- profile policy

Produces:

- durable memory ledger updates
- memory inspection results
- prune or revise actions

## Artifact Manager

Purpose:

- transform memory state into visible symbolic objects and evolution marks

Consumes:

- durable memory
- artifact type registry
- evolution rules
- cosmetic state

Produces:

- artifact records
- portrait unlocks
- shell-visible deltas

## Memory-To-Symbol Mapper

Purpose:

- decide which durable memories deserve visible symbolic consequences

Consumes:

- durable memory ledger
- artifact type registry
- evolution rules
- shell motion and visibility budgets

Produces:

- symbolic mapping decisions
- artifact creation requests
- portrait or shell mutation hints

## Module Loader

Purpose:

- validate and register module packs, portrait packs, and theme packs

Consumes:

- pack manifests
- schemas
- runtime registry config

Produces:

- runtime indexes
- dependency warnings
- resolved registries

## Hybrid Graphics Adapter

Purpose:

- optionally enrich the same scene model for advanced graphics or browser-backed shell surfaces

Consumes:

- capability tier
- scene model
- render budgets

Produces:

- hybrid overlay instructions
- richer event transitions

## Model/Provider Adapter

Purpose:

- isolate model APIs and provider-specific behavior

Consumes:

- normalized inference request
- mode and memory context
- tool policy

Produces:

- normalized inference response
- provider metadata

## Tool/Action Bridge

Purpose:

- isolate external actions, tools, local automation, and auditable side effects

Consumes:

- normalized action request
- safety policy

Produces:

- action result
- audit event

## Persistence Adapter

Purpose:

- isolate storage engine details for sessions, memory, artifacts, and cosmetic state

Consumes:

- typed records
- query requests

Produces:

- stored records
- queried records
- migration hooks

## Import/Export Adapter

Purpose:

- move history, memory, artifacts, and profile state across versions or runtimes

Consumes:

- export or import request
- schema version data

Produces:

- portable bundles
- validation warnings

## Note On Implementation

The first build can implement all of these in one codebase if needed. The important constraint is not process separation; it is contract separation.
