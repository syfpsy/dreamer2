# Slice 3: Atmosphere Engine (World Soul)

## Goal

Prove the soul of the world-generation system. Not every biome. Not full gameplay. One place that feels authored, remembered, and alive, with the companion inside it.

Atmospheric beauty over maximal simulation complexity. Calm, legibility, and a sense that the place carries history outrank spectacle and coverage.

## What Gets Shipped

### One Place End-To-End

- place archetype: `place.signal-chapel`
- layout idiom: `layout.ring-sanctum`
- palette doctrine: `palette.sacred-machine-default`
- motif set: `motif.segmented-ring`, `motif.stepped-halo`, `motif.vow-ring`, `motif.prayer-bracket`, `motif.seam-stitch`
- materials: `material.shrine-plating`, `material.cable-veined-stone`, `material.stitched-membrane`
- weather: `weather.slow-signal-dust`
- scar: `scar.failed-memory-extraction` (conditional on memory state)
- focal: `focal.broken-halo-terminal`
- composition mode: `composition.shrine` with `composition.walker` fallback
- animation behavior modules: `behavior.breath-offset`, `behavior.core-pulse`, `behavior.anchor-pulse`, `behavior.flow-field-drift`, `behavior.ghost-trail`, `behavior.relic-phase`

### Scene Equation Object

A `SceneEquation` object carries:

- `biome_id`
- `layout_idiom_id`
- `focal_object_id`
- `weather_id`
- `scar_ids` (zero or more)
- `agent_state` (mode id)
- `memory_echo_refs` (memory ids contributing echoes)
- `seed` (deterministic)

Every scene holds a reference to the equation that produced it. Regeneration from the equation with the same pack versions reproduces the same scene.

### Semantic Cell Grid

A `SceneGraph` holding a 2D array of `SemanticCell` records (see `WORLD_GENERATION.md`) and a `WorldFieldSet` with at least:

- `signal`
- `memory_resonance`
- `damage`
- `sacredness`

Cells are produced by the pipeline stages, not by the renderer.

### Render Synthesis

A `RenderSynthesizer` consumes a `SceneGraph` and emits a list of `RenderedCell` records carrying glyph, foreground style, background style, density or brightness, animation binding, and optional distortion binding. No glyph is chosen without a semantic cell input.

### Animation Binding

An `AnimationBinder` enumerates scene elements, fetches behavior modules from the registry, validates compatibility per biome and capability tier, and produces a list of active bindings with timing windows and budget cost.

### Pack Registry

A loader that scans `packs/world/archetypes/`, `packs/world/layouts/`, `packs/world/scars/`, `packs/world/focals/`, `packs/world/weather/`, `packs/world/fields/`, `packs/world/materials/`, `packs/style/motifs/`, `packs/style/palettes/`, `packs/animations/`, `packs/companions/dna/`, `packs/companions/lineages/`, and `packs/companions/composition-modes/`, validates against schema, resolves references, and builds immutable registries for the runtime.

## Module Boundaries

New Python modules under `dreamer2_ref/worldgen/`:

- `pipeline.py`: orchestrates the nine stages
- `scene_equation.py`: `SceneEquation` data class and resolver
- `fields.py`: `WorldFieldSet`, field seeding and propagation
- `skeleton.py`: layout idiom instantiation into a cell graph
- `biome.py`: biome grammar loader and constraint enforcement
- `scars.py`: scar package loader and application
- `focal.py`: focal object installation and write-back
- `atmosphere.py`: ambient field and weather simulation
- `integration.py`: companion composition mode application
- `synthesis.py`: `RenderSynthesizer`
- `animation.py`: `AnimationBinder` and the behavior registry bridge
- `registry.py`: pack loader, schema validation, id resolution
- `cells.py`: `SemanticCell` and `SceneGraph` data structures

No existing `dreamer2_ref/*.py` module is rewritten. The shell renderer gains a thin adapter that can accept a `SceneGraph` in addition to the current in-memory frame model. Slice 3 may run the world-gen path in parallel with the current frame and swap at a clean boundary.

## What Does Not Ship In Slice 3

- multiple biomes in the first iteration (only Signal Chapel)
- runtime content hot-reload
- scene export and remix tools
- advanced weather layering
- dual focals
- lineage evolution arcs
- hybrid graphics bloom effects

These are Slice 4+ concerns.

## Acceptance Checks

- `python -m dreamer2_ref --once` renders a Signal Chapel scene with visible focal center of mass, one active ambient weather system, and the companion in shrine mode
- the same invocation with the same seed and pack versions produces the same rendered output
- `soul scars` reflects any scar currently applied; if a failed memory exists, the chapel shows the failed-memory-extraction scar without user command
- no existing tests regress
- added tests cover: scene equation reproducibility, pack registry validation, semantic cell glyph family family constraint, companion composition mode selection fallback, and scar conditional application

## Parallel Path To Current Runtime

Slice 3 adds a `worldgen` subsystem. The existing `app.py` continues to serve the current shell. A new command (proposed: `soul place`) triggers the world-gen pipeline and renders the Signal Chapel scene through the synthesis pass. This lets the soul of the engine be demonstrated without destabilizing the committed Slice 1 and Slice 2 behaviors.

A later slice migrates the main runtime to compose its frame from the semantic scene graph uniformly.

## Implementation Priorities

1. schemas and pack registry with strict validation
2. scene equation object and resolver
3. semantic cell grid and world fields
4. Signal Chapel biome + ring-sanctum layout + slow-signal-dust weather + broken-halo-terminal focal
5. failed-memory-extraction scar with conditional application
6. shrine composition mode with walker fallback
7. animation binding for the six required behaviors
8. render synthesis pass and adapter into the shell renderer
9. the `soul place` command
10. reproducibility tests
