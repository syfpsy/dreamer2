# Glyph Language

## Purpose

One glyph language spans the world and the companion. The place, the agent, the weather, the scars, and the satellites must feel assembled from the same alphabet. Glyph choice is never arbitrary. Every glyph belongs to a family with authored meaning.

This doc formalizes the shared glyph family system referenced throughout `ART_DIRECTION.md`, `PROCEDURAL_ANIMATION.md`, `PORTRAIT_SPEC.md`, `PLACE_GRAMMAR.md`, `ATMOSPHERE.md`, and `ANIMATION_REGISTRY.md`.

## Families

### Structural

Examples: `| / \ _ - [ ] ( ) < >`

Meaning: stable body form, frame geometry, terminal architecture, reliquary casing.

Behavior rules:

- highest persistence
- lowest variance
- used for silhouettes, walls, arches, seams, and frames
- only shifts during meaningful unlocks or damage states

### Soft Signal

Examples: `. , ' : ~`

Meaning: breath, haze, drift, calm listening, low-voltage life, attentive presence.

Behavior rules:

- sparse, slow, low-density
- favored in idle, standby, listening, and peripheral space
- region-bound and cadence-bound

### Dense Pressure

Examples: `# % @ = +`

Meaning: thinking pressure, computation load, focus, construction and synthesis.

Behavior rules:

- used in short bursts
- localized to core, visor, or processing lanes
- must never flood the whole shell

### Decay

Examples: `; ^ x ! ?`

Meaning: corrosion, interrupted signal, memory residue, dream drift, controlled damage.

Behavior rules:

- rare and contextual
- reserved for strain, recovery, unresolved memory, dream states, scar trails
- should read as residue, not random noise

### Symbolic

Examples: `* + o O`

Meaning: ritual marks, relics, unlocks, vows, sacred emphasis.

Behavior rules:

- event-driven
- rare and precise
- brightest importance after stable silhouette
- always carries provenance (source memory, milestone, scar, or ritual event)

## Family Weights Per Biome

Biome grammars declare family weights (see `PLACE_GRAMMAR.md`). Example defaults:

| biome                   | structural | soft-signal | dense-pressure | decay | symbolic |
|-------------------------|------------|-------------|----------------|-------|----------|
| signal-chapel           | 0.45       | 0.30        | 0.08           | 0.07  | 0.10     |
| reactor-crypt           | 0.40       | 0.15        | 0.22           | 0.13  | 0.10     |
| scar-garden             | 0.40       | 0.22        | 0.05           | 0.22  | 0.11     |
| archive-shaft           | 0.48       | 0.24        | 0.08           | 0.10  | 0.10     |
| memory-nursery          | 0.46       | 0.32        | 0.04           | 0.06  | 0.12     |
| soot-basilica           | 0.42       | 0.14        | 0.18           | 0.18  | 0.08     |

The renderer reads these weights during stage 8 (render synthesis) of the world-generation pipeline.

## Companion Glyph Bias

The companion inherits family weights from DNA plus the biome's palette pressure. A companion in a soot-basilica will carry more decay family traces than the same companion in a memory-nursery, without losing identity. This is what makes the agent feel like it belongs to the place.

## Substitution Discipline

Glyph substitution during animation and redraw must remain within family. A structural cell does not suddenly become a decay glyph; a soft-signal drift does not become a dense pressure cluster. Cross-family changes are reserved for events (unlock, scar trigger, dream entry/exit, memory resurfacing) and are always brief and readable.

## Tier Fallbacks

- `pure-text`: prioritize structural and soft-signal families; symbolic glyphs remain but sparsely; decay and dense-pressure are conservative
- `rich-unicode`: broader glyph inventory; subtler distinctions within family allowed; symbolic marks can refine
- `hybrid-graphics`: families may be enriched by non-character elements (glyph-like vector ornaments), but the scene graph still resolves to family semantics

A scene that reads as reverent-chapel in rich Unicode must still read as reverent-chapel in pure text.

## Provenance

Every glyph rendered on screen can be traced back to:

- cell semantic class
- material family
- field values at that cell
- biome family weights
- mode multipliers
- companion DNA bias (if the cell is part of the companion)
- event binding (if the cell is part of an active animation or distortion)

Provenance is not surfaced to the user; it is available for inspection commands (`inspect scene`, `inspect cell`), debugging, and consistency analysis.
