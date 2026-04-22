# Animation Registry

## Purpose

Animation is modular. Every motion in the shell is a named behavior module bound to a target: a cell, a prop, a field, a region, a slot, a scar, a weather system, or the companion itself. Behavior modules are authored content that live in `packs/animations/` and are validated against schema. The renderer does not invent motion; it binds registered behaviors to targets.

See `WORLD_GENERATION.md` stage 9 for how animation runs last in the pipeline, `ATMOSPHERE.md` for motion hierarchy and timing doctrine, and `PORTRAIT_SPEC.md` for slot semantics.

## Behavior Module Shape

A behavior module declares:

- `id`, `label`, `family`
- `target_kinds`: cell, region, field, prop, scar, focal, companion-slot, companion-object, weather
- `input_fields`: which invisible world fields it reads
- `timing`: cadence window (min/max ms), burst window, cooldown
- `glyph_families`: families allowed to animate within the module
- `family_substitution_rules`: within-family replacements only
- `density_cap_override`: optional per-module cap
- `tier_variants`: per capability tier implementations (pure-text, rich-unicode, hybrid-graphics)
- `motion_budget_cost`: low, medium, high
- `compatible_biomes`: biome ids where this module is permitted
- `compatible_materials`: material families where this module is permitted
- `narrative_meaning`: short authored string
- `fallback_behavior_id`: graceful fallback behavior

Modules never hardcode characters. They describe behavior over glyph families and palette roles; the render synthesis pass chooses glyphs within family.

## Behavior Families

### Flow And Drift

- `behavior.flow-field-drift`: vector-guided particle drift along a field axis
- `behavior.directional-lane-flow`: traffic lane drift aligned with layout axis
- `behavior.slow-settle`: sparse falling particles with deceleration
- `behavior.anchor-pulse`: anchored pulse at relay points
- `behavior.orbit-path`: orbital trajectory for companion objects
- `behavior.spiral-drift`: slow inward or outward spiral

### Pulse And Breath

- `behavior.breath-offset`: micro-offset of silhouette cells
- `behavior.core-pulse`: density pulse in core region
- `behavior.edge-softening`: edge contour variance
- `behavior.relay-ping`: single-point ping at cadence
- `behavior.halo-ring-pulse`: ring pulse around halo lane

### Reveal And Scan

- `behavior.scan-line`: horizontal or vertical scan at cadence
- `behavior.reveal-from-noise`: dense-pressure resolves into structural glyph
- `behavior.symbol-resolve`: symbolic glyph fades in from soft-signal
- `behavior.sigil-bloom`: small bloom around a dormant symbol

### Decay And Residue

- `behavior.ghost-trail`: readable echo behind a moved object
- `behavior.ember-fade`: warm decay with slow extinguish
- `behavior.corrosion-creep`: slow cellular spread for scar packages
- `behavior.scan-residue-linger`: lingering mote clusters post-scan
- `behavior.ash-drift`: downward residue near scorched regions

### Symbolic Events

- `behavior.unlock-flare`: brief high-intensity event
- `behavior.relic-phase`: subtle symbolic emphasis
- `behavior.dream-soften`: softened alignment drift, self-resolving
- `behavior.vow-ring-complete`: ring closure animation for a kept vow
- `behavior.lantern-descent`: slow lantern-drop behavior

### Simulation Classes

- `behavior.cellular-spread`: cellular automaton spread for corruption, healing, or resurfacing
- `behavior.reaction-diffusion-bloom`: dream halo or sacred atmosphere bloom
- `behavior.swarm-align`: lightweight swarm for companion satellites
- `behavior.constraint-mutation`: portrait mutation under declared constraints
- `behavior.stitched-return`: slow reassembly of broken elements

## Compatibility Model

Behaviors declare compatibility. The animation binding pass validates every binding against:

- biome permission
- material permission
- capability tier availability
- motion hierarchy slot
- motion budget for the region
- current scene distortion budget

A behavior that fails validation is replaced by its fallback or dropped. Scenes never crash on missing animation; they degrade quietly.

## Binding Pass

During runtime, after the scene graph is composed:

1. enumerate cells, fields, scars, focals, and companion slots
2. for each target with an applicable `motion_tag`, fetch the behavior module
3. check compatibility; if not permitted in this biome or tier, select fallback
4. register the binding with its timing window and budget cost
5. advance the per-region cadence streams

Bindings are stored on the scene graph, not hardcoded in render code. Bindings can be serialized for replay and for diffing.

## Motion Budget Accounting

Each scene holds a motion budget per region. Behavior modules have a cost. The scheduler maintains running totals and refuses to schedule behaviors that would exceed the budget. Rare events (unlock, relic-phase, ritual activation) may temporarily raise the budget through declared authored rules, not through random chance.

## Seeded Randomness Streams

Behaviors read from named randomness streams defined in `WORLD_GENERATION.md`:

- `identity`: blink, breath cadence, orbit style
- `biome_base`: baseline noise
- `scar_events`: damage-spread seeds
- `weather`: drift direction
- `region_noise`: per-region cadence staggering
- `time_phase`: non-looping phase offsets

This keeps motion reproducible per seed while preventing visible loops.

## Graceful Degradation

Every behavior module must declare tier variants or a fallback. In `pure-text`:

- complex substitutions collapse to on/off state changes
- swarm and reaction-diffusion behaviors collapse to anchor-pulse or scan-line equivalents
- gradient-based behaviors collapse to density-only changes

The intent of the behavior survives. The expression shrinks.

## Content Pack Shape

```
packs/animations/<family>/
  <behavior-id>.json          # behavior manifest
```

See `PACK_SYSTEM.md` for composition and load order. Behavior modules are addressable by id from biome grammars, focal object manifests, scar packages, and companion DNA.

## Minimum First Proof

For the first atmosphere-engine vertical slice (`SLICE_3_ATMOSPHERE_ENGINE.md`), only a small set of modules is required:

- `behavior.breath-offset`
- `behavior.core-pulse`
- `behavior.anchor-pulse`
- `behavior.flow-field-drift`
- `behavior.ghost-trail`
- `behavior.relic-phase`

These six are enough to prove invisible-first animation across world and companion.
