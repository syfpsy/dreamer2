# Module Pack Spec

## Purpose

Module packs extend behavior without breaking the base architecture. A module may contribute:

- commands
- panels
- mode affordances
- memory artifact types
- companion entities
- extraction rules
- shell overlays
- ambient field behaviors
- event distortion presets
- border behaviors
- memory artifact renderers
- procedural behavior hooks

## Rules

- A module pack may influence more than one layer, but it must do so through declared contracts.
- A module pack may not directly mutate durable memory outside the memory manager interface.
- A module pack may not bypass command routing or mode policy.
- If a module adds visible evolution, it must declare artifact types and source causes.
- If a module adds procedural rendering behavior, it must declare motion budgets, target layers, and capability fallbacks.

## Pack Shape

Each module pack should declare:

- `id`
- `version`
- `capabilities`
- `commandIds`
- `panelIds`
- `artifactTypeIds`
- `companionIds`
- `ambientBehaviorIds`
- `distortionPresetIds`
- `borderBehaviorIds`
- `artifactRendererIds`
- `overlayIds`
- `optionalModeIds`
- `dependencies`
- `notes`

## Capabilities Taxonomy

- `commands`
- `panels`
- `mode-influence`
- `memory-artifacts`
- `ambient-entities`
- `ambient-field`
- `distortion`
- `border-behaviors`
- `artifact-renderers`
- `dream-hooks`
- `tool-actions`
- `exporters`

## Load Strategy

- load config chooses packs
- module loader validates pack manifest
- registries are composed into runtime indexes
- handlers bind through replaceable interfaces
- render-affecting modules register only through declared scene and renderer hooks

## Suggested Future Pack Families

- ritual core
- archive and ledger
- builder workshop
- research observatory
- dream laboratory
- relic gallery
- system maintenance

## MVP Boundary

For the first slice, only two packs should be live:

- one ritual pack for core commands and panels
- one ledger pack for memory, gallery, and forget flows

Those packs are enough if they also carry:

- one ambient field profile
- one small distortion preset set
- one companion entity
- one memory artifact renderer

The current reference runtime goes one step past that boundary with a small third pack for `building` and `researching` so work-facing modes can be exercised without collapsing the architecture.
