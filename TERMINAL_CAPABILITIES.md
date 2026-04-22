# Terminal Capabilities

## Goal

Gracefully degrade without artistic collapse.

The companion must preserve the same identity across plain ANSI terminals, richer Unicode terminals, browser-based terminal surfaces, and optional advanced graphics environments.

## Capability Detection Inputs

The shell may inspect:

- color depth
- Unicode richness and width behavior
- cursor addressing reliability
- advanced graphics protocol support
- browser or canvas-backed shell surfaces
- performance budget and redraw cost

Capability detection should inform rendering choices. It should not change the product's personality.

## Tier Strategy

### `pure-text`

Use when:

- color support is limited
- Unicode fidelity is unreliable
- redraw cost is high

Behavior:

- structural glyphs dominate
- symbolic and dense glyphs remain sparse
- motion is subtle and mostly region-local
- avoid assumptions about image support or wide glyph fidelity

### `rich-unicode`

Use when:

- Unicode width is trustworthy
- color support is richer
- redraw cost is moderate

Behavior:

- broader glyph families become available
- symbolic marks can be more refined
- ambience can use more nuanced density without clutter

### `hybrid-graphics`

Use when:

- the environment supports richer surfaces or graphics protocols
- performance budget allows richer transitions

Behavior:

- optional cinematic overlays
- event moments may gain more layered treatment
- the same scene model remains authoritative

## Graceful Degradation Rules

- the portrait silhouette must survive every tier
- the text log and command area remain readable first
- core artifacts and symbolic changes must remain legible even in `pure-text`
- hybrid-only affordances may enrich, but may not carry core product meaning alone

## Early Implementation Guidance

Start with:

- an explicit capability detector that returns one of the three tiers
- a shell renderer that consumes the tier as input
- per-tier glyph substitution tables
- per-tier distortion and motion budgets

That is enough to stay future-proof without overbuilding the renderer.
