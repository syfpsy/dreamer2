# Packs

Packs are the data-driven extension surface of the product.

## Module And Style Packs

- `portrait/`: slot-based portrait parts and pack manifests.
- `modules/`: behavioral extension packs for commands, panels, artifacts, and companion entities.
- `themes/`: restrained palette and shell styling definitions.

## World-Generation Packs

- `world/archetypes/`: place archetypes (biome grammars).
- `world/layouts/`: layout idioms (topology families).
- `world/scars/`: story scar packages.
- `world/focals/`: focal object generators.
- `world/weather/`: environmental weather systems.
- `world/fields/`: world field definitions used by the semantic scene graph.
- `world/materials/`: material families.
- `world/scene-equations/`: curated scene equation presets.

## Style Packs

- `style/motifs/`: reusable motif library.
- `style/palettes/`: palette doctrines.

## Animation Packs

- `animations/`: behavior modules, organized by family folder.

## Companion Packs

- `companions/dna/`: companion DNA records.
- `companions/lineages/`: lineage manifests.
- `companions/composition-modes/`: composition mode definitions.

## Rules

Packs should remain declarative. Runtime code should interpret them, not duplicate their logic in hardcoded component trees. See `PACK_SYSTEM.md` for load order, dependency rules, and the full schema map. Every pack is validated at load time against its schema under `specs/schemas/`.
