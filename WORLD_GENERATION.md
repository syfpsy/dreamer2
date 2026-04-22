# World Generation

## Prime Rule

Never generate raw ASCII first. Generate invisible world logic first, then render it into glyphs, color, density, and motion. The renderer is the last pass, not the first.

The source of truth for every scene is a semantic scene graph built from cells, fields, layers, motifs, stories, states, and timings. Randomness must always be constrained by authored rules, seeded identity, biome grammar, visual hierarchy, region behavior, and motion budgets. The rendering pass synthesizes glyphs from that semantic model.

This document defines the invisible-first pipeline. See `PLACE_GRAMMAR.md` for archetypes, `ATMOSPHERE.md` for fields and weather, `COMPANION_ORGANISM.md` for agent-in-scene integration, `ANIMATION_REGISTRY.md` for behavior modules, and `GLYPH_LANGUAGE.md` for the glyph family system shared by world and companion.

## Pipeline Stages

Every scene is produced through nine conceptual stages. Implementations may merge stages for efficiency, but the conceptual boundary must remain crisp and each stage must be inspectable.

### 1. Spatial Skeleton

Generate the architectural graph of the place. Output is a topology: chambers, corridors, voids, focal zones, sealed pockets, overlooks, shafts, ritual bays, machine alcoves, ring loops, branch seams, or any structural primitives required by the chosen layout idiom.

The skeleton records:

- chamber graph with nodes, edges, and adjacency constraints
- dominant axis or radial center if any
- focal zone marker, silence zones, and traffic lanes
- sealed pockets and access policy
- elevation bands or depth tiers if relevant

The skeleton is geometry without meaning. It is mass and void, not material or mood.

### 2. Invisible World Fields

Assign scalar or categorical values per cell, or per region aggregation, for every field the scene needs. No single scene uses every field; biomes declare which fields are in play.

Canonical field set:

- `solidity`, `material`, `age`
- `heat`, `moisture`, `charge`, `radiation`
- `damage`, `corruption`, `dust`
- `signal`, `memory_resonance`, `sacredness`, `machine_influence`
- `traffic`, `exposure`, `growth`, `danger`, `calm`

Fields are evaluated lazily where possible and cached per cell or per region. They are the substrate for later passes: materials bias glyphs, signal density biases ambient motion, sacredness biases motif density, damage biases decay substitutions.

### 3. Biome Grammar

The place-family dictates motif bias, palette discipline, material families, iconography, prop pools, ambient motion style, and symbolic tone. The biome is not a theme; it is a grammar that constrains every later decision.

The biome grammar declares:

- allowed material families and their base ratios
- motif set (see `PLACE_GRAMMAR.md`)
- palette doctrine (see `PALETTE_DOCTRINE.md`)
- allowed ambient weather families
- silence-to-detail ratio
- light doctrine
- glyph-family bias profile
- emotional posture label

A biome is chosen by the scene equation. See `PLACE_GRAMMAR.md` for the starter archetype catalog.

### 4. Story Scars

Apply zero or more past events that have visibly shaped the place. Scars are authored packages that can modify topology, fields, materials, props, ambient behaviors, palette, and motif density.

Examples: reactor burst, cleansing fire, failed repair attempt, archive spill, sentinel nest, ritual lock, field inversion, coolant flood, sabotage breach, dream seep, failed memory extraction, warden purge.

A scar package produces persistent traces that animate subtly under the atmospheric pass. Scars are the primary source of narrative atmosphere. A scene with no scar should feel intentionally pristine, never empty by accident.

### 5. Focal Object Pass

Install one dominant visual and narrative anchor. The focal object claims the compositional center of mass and becomes the local maximum of motion, light, and symbolic density.

Examples: halo terminal, broken altar, data spindle, relay heart, stitched core, coolant lake, watcher tower, containment bloom, suspended archive cage, ritual machine, shrine engine, broken spindle, memory altar, watch core, data loom, starved beacon, coolant mirror, severed crown, ritual furnace.

Each focal object generator declares: dominant motif, compatible biomes, local ambient behaviors, glyph vocabulary, damage logic, interaction affordances, and allowed composition modes for the companion. Scenes without a focal structure must be flagged by the system, not produced by accident.

### 6. Atmospheric Pass

Populate micro-detail: dust, spores, sparks, residue, scan ghosts, dormant symbols, relic fragments, and low-density motion behaviors. This pass uses the field values and biome grammar to seed atmosphere, not to decorate empty space.

Rules:

- detail clusters near meaning (focal, damage, scars, agent, active machinery, memory signatures)
- peripheral space remains sparse
- density is capped per region by biome grammar
- weather systems contribute here (see `ATMOSPHERE.md`)

Negative space is a compositional tool, not a gap to fill.

### 7. Companion Integration

Place the companion inside the scene using a declared composition mode. See `COMPANION_ORGANISM.md` for the mode catalog: `shrine`, `walker`, `projection`, `embedded`, `remote-presence`.

Integration writes back onto the scene: field lines may align toward the agent, dormant symbols may wake, relic fragments may orbit differently, scars may brighten or quiet, shrine motifs may complete themselves. The scene is not static wallpaper.

### 8. Render Synthesis

Convert the semantic scene graph into glyphs, foreground color, background color, brightness or density level, optional per-cell animation behavior, and optional distortion behavior, through a shared visual language.

Render synthesis rules:

- glyph family is determined by cell semantic class, not by random choice
- only meaningful within-family substitutions are allowed
- palette roles are assigned from the biome palette doctrine
- density is interpreted through capability tier (see `TERMINAL_CAPABILITIES.md`)
- the same scene graph must remain emotionally recognizable across capability tiers

The renderer owns style. It does not own meaning.

### 9. Runtime Animation

Apply micro-motion and rare event motion through the timing doctrine (`ATMOSPHERE.md`). Behaviors come from the animation registry (`ANIMATION_REGISTRY.md`) and are bound to cells, props, fields, rooms, scars, or modes.

Animation is the last, most restrained pass. Most of the screen remains stable most of the time. Rare motion and rare accents must matter.

## The Scene Equation

A scene is composed, not randomized. The scene equation is the authored grammar that produces one scene:

```
scene = Biome + StoryEvent + Mood + FocalObject + EnvironmentalWeather + ScarType + AgentState + MemoryEcho
```

Example:

```
ArchiveShaft + failed-memory-extraction + reverent-instability + broken-halo-terminal + slow-signal-dust + stitched-burn-seam + listening-agent + recurring-user-memory-echo
```

One line is enough to derive palette, room graph, prop density, ambient field behavior, relic placement, distortion chance, and agent posture. Preserve this convention in the architecture. Scenes are generated from story-rich descriptors, not only from seeds and tile noise.

The scene equation is a first-class object. Every scene keeps a reference to its equation so the system can regenerate, remix, diff, share, and inspect scenes by story rather than by coordinate.

## Semantic Cells

The world is a grid of semantic cells, not a grid of characters. A cell is the smallest addressable unit of meaning.

Cell attributes:

- `type`: floor, wall, void, arch, seam, niche, altar, shaft, vent, pool, cable-run, etc.
- `material`: reference to the material language (`MATERIAL_LANGUAGE.md` in `PLACE_GRAMMAR.md`)
- `elevation` (optional): for layouts that use vertical bands
- `openness`: 0..1 scalar for visibility and traversal
- `light_exposure`: 0..1 scalar; biased by focal, weather, and scars
- `damage`, `heat`, `signal`, `memory_resonance`, `corruption`, `sacredness`: field values
- `prop_occupancy`: reference to a prop descriptor if any
- `active_state`: inert, humming, pulsing, ignited, sealed, ritual-active, corrupted, mourning, etc.
- `motion_tag`: registry key from the animation registry; may be empty
- `dominant_influences`: ordered references to nearby focal objects, scars, sentries, the companion, or weather systems that bias this cell

Rendering reads the cell and produces:

- `glyph`: chosen from the cell's biased glyph family
- `foreground_style`, `background_style`: from palette roles
- `brightness_or_density`: tier-aware
- `animation_binding`: optional behavior module reference
- `distortion_binding`: optional distortion preset reference

The cell model is renderer-independent. A cell can be serialized, diffed, exported, or mutated without touching glyph choice.

## Invisible Field Model

A world field is a value over space and time. Fields are authored with the following metadata:

- `id`
- `kind`: scalar, categorical, vector, boolean
- `range` or `domain`
- `source_rules`: how the field is seeded (from focal, scar, weather, companion, biome base)
- `propagation_rules`: diffusion, falloff, directional flow, clustered, sealed
- `decay_rules`: time-based decay, event-based decay, or stable
- `consumers`: which render decisions or behavior modules read it

Fields enable emergent composition. For example, `signal` may be seeded high at the focal terminal, diffuse down the central axis of a relay spine, and be dampened by scar packages of type `sentinel purge`. The atmospheric pass then samples `signal` to decide where soft-signal glyphs drift and where dense pressure glyphs cluster, without any single line of code saying "place drift here."

## Multi-Pass Runtime Simulation

The conceptual runtime loop:

1. update story state and mode state
2. update long-lived scene fields
3. advance deterministic seeded randomness streams
4. update local behavior modules and timers
5. update ambient field simulation
6. update companion micro-motion and slot states
7. update event animations
8. update memory-driven symbolic consequences
9. compose semantic render layers into the scene graph
10. synthesize glyphs, colors, and substitutions from cell states and layer influences
11. compute diff from prior frame
12. redraw only changed cells or regions where possible

The loop is renderer-agnostic. The source of truth is the scene graph, not the terminal output.

## Determinism Streams

Randomness is partitioned into named streams, each seeded deterministically:

- `identity`: from the companion seed and user profile
- `biome_base`: from the biome id and scene seed
- `scar_events`: one stream per scar package
- `weather`: per weather system
- `region_noise`: per spatial region for staggered cadence
- `time_phase`: wall-clock offsets for non-looping motion

Streams advance in the runtime loop in a defined order so scenes remain reproducible given the same seed and equation. Non-deterministic user input may affect equations but not the stream order.

## Memory-In-World

Memory echoes can surface in the world, not only in the companion. A recurring user concern may become a faint repeated motif in walls. A solved problem may become a dormant shrine that lights softly when the scene is generated. An old scar may appear as stitched seams in a corridor the companion has never named.

Promotion rules live in `MEMORY_MODEL.md` (extended). The world-generation side treats memory echoes as:

- motif bias toward the echoed motif family
- field seed: `memory_resonance` locally raised
- optional dormant symbol placement near the focal object
- occasional scar-echo at reduced intensity

Memory-in-world must never break biome grammar. The biome remains the top-level constraint.

## What This Is Not

- Not a tile-soup map generator.
- Not a random character collage.
- Not a roguelike dungeon generator.
- Not a static ASCII illustration tool.

It is a procedural atmosphere engine for a living terminal companion. Every place is a chamber of memory, signal, weather, and machine history. Every visual decision reinforces the sensation that the companion and the world are co-authored by the same quiet, ancient, evolving machine logic.

## Minimum First Proof

The first vertical slice for this layer should only prove the soul. See `SLICE_3_ATMOSPHERE_ENGINE.md` for the concrete implementation plan. The goal is not to ship every biome. The goal is to ship one place that feels authored, remembered, and alive, with the companion inside it.
