# World Generation Index

Quick-map index for the world-generation doctrine. Read these in order for a full picture.

## Doctrine

1. `WORLD_GENERATION.md` — invisible-first pipeline, scene equation, semantic cells, world fields, determinism streams, memory-in-world
2. `PLACE_GRAMMAR.md` — place archetype catalog, layout idioms, material language, motif library, palette doctrine, silence ratios
3. `ATMOSPHERE.md` — ambient fields, environmental weather, distortion discipline, motion hierarchy, timing doctrine
4. `COMPANION_ORGANISM.md` — companion DNA, lineages, composition modes, companion objects, mutation rules
5. `ANIMATION_REGISTRY.md` — modular behavior classes, compatibility model, binding pass, motion budget accounting
6. `GLYPH_LANGUAGE.md` — shared glyph family system across world and companion
7. `PACK_SYSTEM.md` — composable content packs for every content class; load order; dependency and conflict rules

## Planning

- `SLICE_3_ATMOSPHERE_ENGINE.md` — first vertical slice to prove the world-generation soul

## Existing Anchor Docs (still authoritative)

- `ARCHITECTURE.md` — layers, runtime flow, replaceable interface boundaries (extended)
- `ROADMAP.md` — slice plan (extended with Slice 3 Atmosphere Engine)
- `MEMORY_MODEL.md` — memory categories, promotion, symbolic mapping, world echoes (extended)
- `ART_DIRECTION.md` — doctrine, stability ratio, glyph families, palette discipline
- `PORTRAIT_SPEC.md` — slot anatomy, procedural zones, layers, mutation constraints
- `PROCEDURAL_ANIMATION.md` — capability tiers, motion hierarchy, timing doctrine, ambient field behaviors, memory-to-visual mapping
- `COMMAND_MAP.md` — command grammar and domains
- `MODULE_SPEC.md` — module pack contract
- `TERMINAL_CAPABILITIES.md` — capability detection and tier strategy
- `PLAN.md` — non-negotiables and minimum proof

## Content Packs (under `packs/`)

- `packs/world/archetypes/` — place archetypes
- `packs/world/layouts/` — layout idioms
- `packs/world/scars/` — story scar packages
- `packs/world/focals/` — focal object generators
- `packs/world/weather/` — environmental weather systems
- `packs/world/fields/` — world field definitions
- `packs/world/materials/` — material families
- `packs/world/scene-equations/` — curated scene equation presets
- `packs/style/motifs/` — motif library
- `packs/style/palettes/` — palette doctrines
- `packs/animations/` — behavior modules
- `packs/companions/dna/` — companion DNA records
- `packs/companions/lineages/` — lineage manifests
- `packs/companions/composition-modes/` — composition modes
- `packs/modules/` — existing module packs (behavior/commands/panels)

## Schemas (under `specs/schemas/`)

All packs validate against JSON schemas under `specs/schemas/`. See `PACK_SYSTEM.md` for the class-to-schema map.

## Prime Rule

Never generate raw ASCII first. Generate invisible world logic first, then render it. The renderer is the last pass, not the first.
