# Portrait Spec

## Core Principle

The portrait is a composable anatomical system, not one giant ASCII file.

It should be rendered as a stable identity inside a procedural cell field. The portrait may deform, breathe, flicker, and accrue symbolic changes, but it must remain recognizable first and variable second.

## Slots

Minimum slot set:

- `head`
- `eyes`
- `jaw`
- `shoulders`
- `core`
- `halo`
- `overlay`
- `scar`
- `relic`
- `companion`
- `environment`

Not every composition needs every slot active, but each slot must have fallback behavior.

## Stability Doctrine

The portrait begins from an iconic base silhouette. Approved procedural change is constrained by:

- approved zones
- approved intensity ranges
- active mode
- identity seed
- event budget

Disallowed behavior:

- full silhouette scrambling
- constant whole-face mutation
- noisy independent motion on every slot

## Procedural Zones

Approved zones for constrained mutation:

- eyes: flicker, scan, slight aperture shifts
- visor or face frame: density or scan emphasis
- jaw: minimal tension or release shifts
- halo: flicker, ring pulse, dream haze
- scar layer: activation or warmth during recovery
- relic layer: orbit, hover, symbolic reveal
- outer contour: slight breathing or edge softness

The portrait center should remain more stable than the edges.

## Layers

Render passes should be composed in this order:

1. silhouette
2. facial and core identity
3. micro-motion layer
4. ambient field and environmental glyphs
5. mode overlays
6. symbolic event layer

## Part Contract

Each portrait part should declare:

- slot
- dimensions and anchor points
- glyph families
- palette role and palette hints
- frame or generation rules
- per-state behavior
- procedural behavior hooks
- animation personality
- mutation constraints
- unlock rules
- fallback part
- narrative meaning

## State Behavior

Parts may behave differently in:

- `standby`
- `listening`
- `thinking`
- `building`
- `researching`
- `dreaming`
- `recovering`
- `focused`

The same part should remain identifiable across states. States should modulate motion, signal density, and overlays before they replace identity.

## Motion Doctrine

Allowed micro-motion:

- slow breathe offset
- eye flicker
- scan line drift
- subtle pulse
- rare orbit path advance

Rare event motion:

- short glitch
- unlock flare
- dream distortion
- memory resurfacing shimmer

Procedural motion should be driven by constraints, not raw randomness. Family substitutions, density changes, local offsets, and reveal timing are preferred over wholesale redraw.

## Procedural Generation Rules

Use four controlled randomness categories:

- seeded identity randomness
- state-based randomness
- region-based randomness
- time-based randomness

Every procedural decision should declare which categories it uses and what its intensity ceiling is.

## Glyph Discipline

Portrait parts should declare compatible glyph families so substitutions remain semantically coherent:

- structural glyphs for silhouette and frame
- soft signal glyphs for breath, halos, and low-energy motion
- dense pressure glyphs for thinking load
- decay glyphs for dream drift, damage, or repair
- symbolic glyphs for relics, sigils, and unlock marks

## Capability Fallback

Every portrait behavior should degrade cleanly across capability tiers:

- `pure-text`: prioritize silhouette, eye signal, core pulse, and one symbolic mark
- `rich-unicode`: allow denser texture and finer symbolic detail
- `hybrid-graphics`: allow richer overlays without replacing the slot model

## Evolution Doctrine

Portrait evolution should accumulate in small visible truths:

- scars from recovered strain
- relics from preserved meaning
- halo refinements from trust and continuity
- core adornments from sustained building or craft

The stable silhouette should change last, not first.

## Fallback Strategy

Every slot must support:

- explicit fallback part
- empty-state behavior if no part is unlocked
- safe palette fallback if a theme is missing
- static render fallback if animation is disabled
