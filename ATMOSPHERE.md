# Atmosphere

## Purpose

Atmosphere is world behavior, not decoration. It is expressed through invisible fields and behavior layers that run with discipline. This doc defines ambient field systems, environmental weather, distortion discipline, and motion hierarchy. All atmospheric systems obey the scene equation and biome grammar; nothing here is free-roaming.

See `WORLD_GENERATION.md` for the field model, `PLACE_GRAMMAR.md` for biome declarations, `ANIMATION_REGISTRY.md` for the behavior modules that animate atmosphere, and `GLYPH_LANGUAGE.md` for the glyph families atmosphere uses.

## Ambient Field Systems

Ambient fields are the low-energy life of a scene. Each is defined declaratively. No scene uses every field.

Starter ambient field systems:

- `ambient.signal-drift`: coherent slow drift lines in a dominant axis
- `ambient.scan-residue`: lingering post-scan motes
- `ambient.memory-dust`: sparse soft-signal points near memory_resonance
- `ambient.heat-shimmer`: subtle substitution near heat peaks
- `ambient.sacred-halo-bloom`: occasional soft bloom near sacredness peaks
- `ambient.charge-sparks`: rare decay-family flickers near charge peaks
- `ambient.coolant-mist`: broad low-density haze in cooling-glass or wet-alloy regions
- `ambient.ash-drift`: slow downward residue near scorched-polymer and soot
- `ambient.anomaly-pollen`: rare symbolic marks near rare_anomaly peaks
- `ambient.whispering-static`: very rare dense-pressure bursts at field edges

Each ambient field declares:

- `id`, `label`
- `field_inputs`: which world fields bias it (signal, memory_resonance, heat, etc.)
- `region_targets`: negative space, portrait edge, panel seams, halo lane, far field, mid field, memory surface, panel edge
- `glyph_families`: allowed families, weighted
- `density`: base density, capped by biome silence ratio
- `cadence_window_ms`: min/max per-stream cadence
- `simulation_class`: flow-field, anchored-pulse, directional-flow, residue-drift, stitched-return, vector-lane, beacon-scan, held-stillness
- `mode_multipliers`: per companion mode
- `weather_compatibility`: weather systems it coexists with

Ambient fields respond to mode. Standby is sparse and watchful. Thinking introduces directional scan energy. Dream loosens geometry. Recovery reorganizes. Stress hardens edges. All of this must remain restrained and readable.

## Environmental Weather Systems

Weather is procedural and symbolic. It is sparser than ambient fields but more shaped. Weather claims its own density budget and can dominate a sub-region.

Starter weather systems:

- `weather.slow-signal-dust`: broad soft-signal dust, gentle directional bias, long cadence
- `weather.data-snow`: symbolic pinpoints falling through a vertical axis
- `weather.static-mist`: dense-pressure murmur at the far field
- `weather.cinder-fall`: decay descent with rare ember motifs
- `weather.resonance-ripples`: concentric ring pulses radiating from focal
- `weather.ghost-trails`: intermittent trails along traffic lanes
- `weather.charge-motes`: small symbolic points clustering at charge peaks
- `weather.ember-drift`: warm rare-anomaly dots drifting horizontally
- `weather.dream-pollen`: symbolic blooms appearing and dissolving softly
- `weather.null-current`: negative field that dampens adjacent ambient behaviors

Each weather system declares:

- `id`, `label`
- `dominant_axis`: vertical, horizontal, radial, none
- `density_budget`: absolute cap and per-region cap
- `glyph_families`: allowed families
- `palette_roles`: allowed roles
- `interaction_with_agent`: attract, repel, ignore, align
- `interaction_with_focal`: amplify, dampen, halo, stitch, none
- `compatible_biomes`: biome ids

Weather must be sparse enough to preserve readability and strong enough to lend identity. Never snowstorm the screen.

## Distortion Discipline

Distortion is ceremonial. It is powerful only when rare and meaningful. Every scene carries a glitch budget that is mostly unspent.

Starter distortion presets:

- `distortion.clear`: no active distortion, default
- `distortion.breath`: tiny cadence jitter on arrival or pause
- `distortion.strain`: dense interruption under pressure
- `distortion.dream-soft`: softened alignment drift with quick self-resolution
- `distortion.relic-phase`: subtle symbolic emphasis when an artifact surfaces
- `distortion.edge-slippage`: edges desynchronize briefly
- `distortion.ghost-trail`: readable echo behind a moved object
- `distortion.phase-bleed`: color role bleeds one step toward rare_anomaly
- `distortion.line-tear`: rare tear across a single row, resolves within a beat
- `distortion.symbol-echo`: symbolic glyph reappears faintly at delayed cadence

Each preset declares:

- `trigger_kinds`: wake, dream-enter, dream-exit, memory-resurfacing, artifact-reveal, strain, sentinel-proximity, ritual-activation, transmission-failure
- `readability_floor`: minimum readability maintained
- `max_duration_ms`
- `glyph_families`: families allowed to mutate within the preset
- `glitch_budget_cost`: low, medium, high
- `tier_overrides`: per capability tier

Rules:

- most sessions remain stable
- never stack distortions casually
- readability always outranks spectacle
- distortions resolve within a few beats and leave no residue unless the scene's scar package explicitly allows it

## Motion Hierarchy

Motion is not free. Every scene declares a motion budget per region. The center of the companion is more stable than the edges. The focal object is more active than the quiet corners (unless the scene is intentionally distance-centered). Panels and readable text surfaces animate less than atmospheric layers.

Hierarchy ceiling, from most stable to most active:

1. command area and prompt (no motion beyond cursor)
2. text panels and logs (low, append-only)
3. portrait center and silhouette (low, breath-like)
4. biome architecture and walls (very low)
5. portrait edges and mode overlays (low-medium)
6. companion satellites and relic orbits (medium)
7. focal object local behaviors (medium)
8. ambient fields (medium, distributed)
9. weather systems (medium, sparse)
10. event animations (high, rare)
11. distortion events (high, ceremonial)

The system must enforce this hierarchy. A scene may request specific exceptions, but they must be authored in the biome grammar or focal object manifest, not set by random chance.

## Timing Doctrine

- prefer slow irregular rhythms over perfect loops
- stagger cadence by region so the screen never blinks in unison
- use variable timing windows, burst windows, and cooldowns
- most frames produce small deltas; large deltas are reserved for events
- cadence ranges per subsystem:
  - shell frame cadence: 80-160 ms
  - ambient cadence windows: 400-3000 ms per region
  - event bursts: under 1200 ms
  - dream drift: slow and non-uniform
  - distortion: under 1100 ms with self-resolve

The animation registry binds behavior modules into these windows. See `ANIMATION_REGISTRY.md`.

## Scene Reactivity To The Companion

The place is not static wallpaper. Nearby field lines align toward the agent. Dormant symbols wake when the agent lingers. Relic fragments orbit differently when the companion's mode shifts. Damage seams brighten near an agent in recovery. Shrine motifs complete themselves when the agent is in a ritual-coherent state. Signal drift becomes coherent when the companion is listening. Certain scars quiet down when the agent is calm.

These reactions are declared in the biome grammar and focal object manifests as `companion_bias_rules`. They never override the biome's silence budget or palette doctrine.

## Graceful Degradation

Atmosphere must survive capability tiers. In `pure-text`, weather systems degrade to their dominant axis and primary glyph family, ambient fields reduce density, and distortion presets use timing-only variants where character substitutions would not read. In `rich-unicode`, atmosphere gains nuance but not new meaning. In `hybrid-graphics`, atmosphere may bloom visually without changing what the scene is about.

The scene equation remains the source of truth. The atmosphere shrinks; it never disappears.
