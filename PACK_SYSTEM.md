# Pack System

## Purpose

Every piece of authored content is a composable pack. The runtime never hardcodes biomes, materials, motifs, animations, weather, scars, focals, layouts, palettes, lineages, or companion DNA. Packs are read at load time, validated against schema, indexed into registries, and referenced by id throughout the scene equation and the render pipeline.

This extends the module pack system in `MODULE_SPEC.md` to cover every content class added by world generation. Module packs retain their semantics; world-generation packs are a parallel family indexed into the same registry architecture.

## Content Classes

Each class ships as a pack family with its own schema and loader:

| class                  | folder                                   | schema                                                                 |
|------------------------|------------------------------------------|------------------------------------------------------------------------|
| place archetype        | `packs/world/archetypes/`                | `specs/schemas/world/place-archetype.schema.json`                      |
| layout idiom           | `packs/world/layouts/`                   | `specs/schemas/world/layout-idiom.schema.json`                         |
| scar package           | `packs/world/scars/`                     | `specs/schemas/world/scar-package.schema.json`                         |
| focal object           | `packs/world/focals/`                    | `specs/schemas/world/focal-object.schema.json`                         |
| weather system         | `packs/world/weather/`                   | `specs/schemas/world/weather-system.schema.json`                       |
| world field            | `packs/world/fields/`                    | `specs/schemas/world/world-field.schema.json`                          |
| material               | `packs/world/materials/`                 | `specs/schemas/style/material.schema.json`                             |
| motif                  | `packs/style/motifs/`                    | `specs/schemas/style/motif.schema.json`                                |
| palette doctrine       | `packs/style/palettes/`                  | `specs/schemas/style/palette-doctrine.schema.json`                     |
| animation behavior     | `packs/animations/`                      | `specs/schemas/animation/behavior-module.schema.json`                  |
| companion DNA          | `packs/companions/dna/`                  | `specs/schemas/portrait/companion-dna.schema.json`                     |
| lineage                | `packs/companions/lineages/`             | `specs/schemas/portrait/lineage.schema.json`                           |
| composition mode       | `packs/companions/composition-modes/`    | `specs/schemas/portrait/composition-mode.schema.json`                  |
| scene equation preset  | `packs/world/scene-equations/`           | `specs/schemas/world/scene-equation.schema.json`                       |
| module                 | `packs/modules/`                         | existing `MODULE_SPEC.md` contract                                     |

Each pack folder holds one or more manifests. Manifests declare `id`, `version`, and the class-specific payload. Ids are namespaced (`place.signal-chapel`, `scar.failed-memory-extraction`, `behavior.flow-field-drift`).

## Registry Model

A pack registry is built at startup:

1. scan pack folders
2. validate each manifest against its schema
3. resolve references (e.g., a biome's `allowed_scar_packages` must exist)
4. reject packs that fail validation, with structured errors
5. expose lookup by id and enumeration by class

Registries are immutable during a single runtime loop. Hot reload may rebuild the registry between loops for content work.

## Dependency And Conflict Rules

- A pack may declare `dependencies` on other pack ids.
- A pack may declare `conflicts_with` for incompatible content.
- Biomes are never implicitly overridden. Theme packs remap palette roles but cannot change biome semantics.
- A lineage can extend another lineage through `extends`, inheriting motifs and silhouette intent.
- A scar package can declare `affinity_biomes` and `incompatible_biomes`.

## Load Order

1. schemas (built-in, not a pack)
2. world fields
3. materials
4. motifs
5. palette doctrines
6. animation behavior modules
7. layout idioms
8. weather systems
9. focal objects
10. scar packages
11. place archetypes
12. lineages
13. composition modes
14. companion DNA
15. scene equation presets
16. module packs (`MODULE_SPEC.md`)

This order is authored so later content classes can reference earlier ones without forward references. Validation enforces this.

## Minimum Manifest Fields

Every pack manifest must include:

- `id`: namespaced
- `version`: semver
- `class`: content class tag
- `title`: short human label
- `notes`: optional authored description
- class-specific payload

## Authoring Rules

- Packs are JSON, not code.
- Packs never embed raw character art. They declare glyph families, palette roles, motif references, and material references.
- Packs may contain fallback references so degradation is graceful.
- Packs should be small and single-purpose.
- A scene equation preset is a first-class pack that references a place archetype, a scar, a focal, a weather, a layout idiom, and an agent composition mode. It is the authored entry point for a scene and enables curated story-rich scenes.

## Community-Safe Defaults

A pack from an untrusted source may not:

- add new distortion presets beyond declared glitch budget caps
- exceed motion budget caps
- redefine palette role semantics
- mutate durable memory
- bypass command routing or mode policy

These are enforced at validation time. Trusted first-party packs may extend the set of presets and budgets, but the defaults remain safe.

## Content Versioning

- Pack versions follow semver.
- Scenes store the pack versions that produced them.
- A scene may be regenerated from an equation with the same versions and reproduce the same output.
- A later version of a pack must be able to regenerate earlier scenes with the same emotional posture, within authored migration rules.

## Relationship To Module Packs

Module packs (`MODULE_SPEC.md`) add behavior, commands, and panels. World-gen packs add content. A module pack may declare it requires certain world-gen content classes to be present (for example, a dream module may require a `weather.dream-pollen` system). This is declared via `dependencies` referencing content pack ids.
