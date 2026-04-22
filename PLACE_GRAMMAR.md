# Place Grammar

## Purpose

A biome or place archetype is a grammar, not a theme. It constrains every downstream decision so a scene from the same archetype feels like a sibling of every other scene from that archetype, regardless of seed.

Each archetype declares its material vocabulary, motif set, damage style, silence-to-detail ratio, light doctrine, ambient motion doctrine, glyph-family bias, and emotional posture. It never declares specific characters.

This doc defines: the starter archetype catalog, the layout idiom catalog, the motif library, the material language, and the palette doctrine. Scar packages and focal object generators have their own docs (`SCAR_PACKAGES.md` and `FOCAL_OBJECTS.md`, referenced inside this doc).

## Archetype Definition

A place archetype declares:

- `id`, `label`, `emotional_posture`
- `compatible_layout_idioms`: references into the layout catalog
- `material_families`: ordered list with base ratios
- `motif_set`: references into the motif library
- `glyph_family_bias`: weights across the five glyph families
- `palette_doctrine_ref`: structural / dim / energy / rare-anomaly
- `allowed_ambient_fields`: references from `ATMOSPHERE.md`
- `allowed_weather_systems`: references from `ATMOSPHERE.md`
- `allowed_scar_packages`: references from `SCAR_PACKAGES.md`
- `allowed_focal_objects`: references from `FOCAL_OBJECTS.md`
- `allowed_composition_modes`: references from `COMPANION_ORGANISM.md`
- `silence_to_detail_ratio`: 0..1, how much of the place should remain sparse
- `light_doctrine`: reverent, industrial, cold, dreamlit, scorched, quiet, flooded, etc.
- `motion_budget`: per-region caps used by the atmospheric pass and animation registry
- `notes`

Archetypes are content, not code. They live in `packs/world/archetypes/` as JSON manifests validated against `specs/schemas/world/place-archetype.schema.json`.

## Starter Archetype Catalog

The following archetypes are the authored starter set. Implementations add manifests as the world grows; no archetype is hardcoded in the renderer.

| id                            | label                 | emotional posture                |
|-------------------------------|-----------------------|----------------------------------|
| `place.signal-chapel`         | Signal Chapel         | reverent, attentive              |
| `place.relay-tomb`            | Relay Tomb            | sealed, grieving                 |
| `place.reactor-crypt`         | Reactor Crypt         | deep, dangerous, holy            |
| `place.scar-garden`           | Scar Garden           | stitched, convalescent           |
| `place.flooded-switchyard`    | Flooded Switchyard    | still, reflective, quietly alive |
| `place.archive-shaft`         | Archive Shaft         | vertical, remembering            |
| `place.warden-hangar`         | Warden Hangar         | watchful, industrial             |
| `place.halo-vault`            | Halo Vault            | sacred, crowned, still           |
| `place.memory-nursery`        | Memory Nursery        | tender, vulnerable               |
| `place.quiet-observatory`     | Quiet Observatory     | distant, listening               |
| `place.proxy-forge`           | Proxy Forge           | hot, laborious, unfinished       |
| `place.stitched-cavern`       | Stitched Cavern       | repaired, uneasy                 |
| `place.hollow-junction`       | Hollow Junction       | crossroads, haunted              |
| `place.soot-basilica`         | Soot Basilica         | cathedral, scorched              |
| `place.null-reservoir`        | Null Reservoir        | absent, absorbing                |
| `place.choir-engine`          | Choir Engine          | chanting, mechanical             |
| `place.ember-array`           | Ember Array           | hot points, patient              |
| `place.lantern-trench`        | Lantern Trench        | lit path, dim edges              |

Each archetype produces many variants from the same grammar: different scars, different focals, different weather, different layout idioms, different motif rotations. The identity of the place holds.

## Layout Idiom Catalog

A layout idiom is a topology family. The scene equation chooses an idiom compatible with the biome and focal object.

| id                              | shape                                     |
|---------------------------------|-------------------------------------------|
| `layout.chamber-complex`        | small interconnected rooms                |
| `layout.vertical-shaft`         | tall narrow drop with balconies           |
| `layout.ring-sanctum`           | circular chamber around a focal           |
| `layout.relay-spine`            | long central corridor with ribs           |
| `layout.branching-trenches`     | trench system with forks                  |
| `layout.radial-shrine`          | radial nave around a center altar         |
| `layout.broken-grid`            | grid with collapsed or sealed cells       |
| `layout.single-hall`            | one giant hall with niches                |
| `layout.machine-garden`         | distributed machine islands               |
| `layout.amphitheater`           | tiered ring looking inward                |
| `layout.containment-grid`       | sealed cells in a structured array        |
| `layout.observatory-lens`       | concentric arcs opening outward           |
| `layout.flooded-lattice`        | sparse islands on a reflective plane      |

Idioms are grammars for topology. The spatial skeleton pass instantiates an idiom into concrete nodes and edges. Idioms are declarative and renderer-independent.

## Material Language

Materials bias glyph choices, density, edge treatment, and allowed animation behaviors. Biome grammars declare which material families are allowed and in what base ratios.

Starter material families:

- `oxidized-steel`: stressed structural lines, muted corrosion, occasional rivet motifs
- `ash-concrete`: coarse silent mass, low reflectivity, little animation
- `cable-veined-stone`: structural with embedded signal seams
- `shrine-plating`: clean, stable, near-silent
- `wet-alloy`: subtle shimmer, reflective
- `dusted-ceramic`: pale, matte, fragile feel
- `scorched-polymer`: broken high-contrast substitutions, rare sparks
- `signal-moss`: soft irregular low-frequency motion
- `bone-white-archive-shell`: chalked, brittle, sacred
- `cooling-glass`: translucent, humming, very quiet
- `stitched-membrane`: seams, mended lines, active in recovering states
- `ancient-machine-brass`: patinated, warm dim tones, heavy

Each material declares:

- `allowed_glyph_families` with weights
- `edge_treatment`: sharp, dusted, cracked, seam, smooth, rippled
- `preferred_density_curve`
- `preferred_palette_roles`
- `animation_compatibility`: which animation behaviors may bind to cells of this material
- `scar_affinity`: which scar packages feel natural on this material

Materials are packaged under `packs/world/materials/`.

## Motif Library

Motifs are small repeating formal patterns that make procedural worlds feel authored. Biomes and companion lineages each declare a small motif set. Repetition is the source of coherence.

Starter motifs:

- `motif.segmented-ring`
- `motif.eye-window`
- `motif.cable-ladder`
- `motif.cruciform-joint`
- `motif.prayer-bracket`
- `motif.nested-rectangles`
- `motif.stepped-halo`
- `motif.data-rivet`
- `motif.spine-arch`
- `motif.seam-stitch`
- `motif.vow-ring`
- `motif.ember-dot`
- `motif.lantern-drop`
- `motif.relay-pylon`
- `motif.containment-clasp`

Motifs live in `packs/style/motifs/` and can be applied across world generation, companion generation, and UI ornamentation. A motif declares its recognizable silhouette rule, compatible materials, compatible glyph families, rotation/mirroring permissions, and narrative meaning.

A motif is a rule, not a character. The renderer chooses characters at synthesis time, within family.

## Palette Doctrine

A place relies on four palette roles:

- `structural`: one main structural color family
- `dim_support`: one dim support family
- `energy_or_event`: one energy or event family
- `rare_anomaly`: one rare anomaly family

Biomes declare allowed ranges for each role and contrast rules. The companion shares the same palette doctrine so it reads as an emissary of the place, not a pasted portrait. Theme packs may remap palette roles but not their semantic meaning.

Color is language:

- `structural` carries mass and silence
- `dim_support` carries negative space and far air
- `energy_or_event` carries signal, life, warning, information
- `rare_anomaly` carries ritual, relic, dream, sacredness, unlock, corruption peak

Rainbow noise is disallowed. Accent colors appear only for named events.

## Silence-To-Detail Ratio

Every biome declares a target silence-to-detail ratio. The atmospheric pass uses this to cap density per region. The rule: detail clusters near meaning; peripheral space remains sparse. Motion is even more restrained than static detail.

Example starter defaults:

- `place.signal-chapel`: 0.72 silence
- `place.reactor-crypt`: 0.62
- `place.scar-garden`: 0.68
- `place.archive-shaft`: 0.74
- `place.memory-nursery`: 0.78
- `place.soot-basilica`: 0.66
- `place.ember-array`: 0.60

Numbers are starting points; they are authored, not random.

## Composition Rules

- A biome chooses one dominant layout idiom per scene.
- A biome allows a small curated set of scar packages; the scene equation chooses zero or more.
- Every scene installs exactly one focal object by default; rare archetypes may permit dual focals with declared tension rules.
- Motif density must not exceed the biome's authored cap.
- Palette roles are never used outside their role.
- Materials are never mixed without an authored transition motif (seam, clasp, trench, arch, etc.).

## Content Pack Shape

Each archetype ships as:

```
packs/world/archetypes/<archetype-id>/
  place.json                  # archetype manifest
  variants/*.json             # optional named variants biasing fields, weather, or motifs
```

See `PACK_SYSTEM.md` for the general composable pack structure.
