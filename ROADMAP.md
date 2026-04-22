# Roadmap

## Vertical Slice 1: First Presence

Goal: prove the soul of the product.

Ship:

- capability-aware shell renderer with `pure-text` support first
- diff-based redraw or equivalent efficient region update abstraction
- one portrait pack and one theme
- stable iconic portrait with seeded identity profile
- ambient field with calm low-density motion
- command input with `send`, `help`, `soul`
- `standby` and `listening` modes
- persistent profile and session seed
- recent memory surface
- one symbolic memory artifact that visibly changes the shell or portrait
- one companion object or orbiting relic

Exit criteria:

- the companion feels recognizable after reopening the app
- one remembered event creates one visible artifact or portrait reaction
- the two starter modes feel visibly distinct without becoming noisy

## Vertical Slice 2: Dream And Recall

Ship:

- dream behavior with restrained geometric loosening
- controlled distortion events for wake, dream ingress, or memory resurfacing
- memory-driven portrait mutation in approved zones only
- durable memory ledger
- inspect, revise, and forget flow
- session-to-session preference carryover
- gallery timeline with first snapshots and milestones
- `memory`, `gallery`, and `forget` commands

## Vertical Slice 3: Atmosphere Engine (World Soul)

Goal: prove the world-generation soul. Not every biome, not full gameplay. One place that feels authored, remembered, and alive, with the companion inside it.

Ship:

- scene equation object resolved per scene
- semantic cell grid with a minimal field set (`signal`, `memory_resonance`, `damage`, `sacredness`)
- one place archetype manifest (Signal Chapel) with palette doctrine, motif set, material families, and silence ratio
- one layout idiom (ring-sanctum) instantiated from the archetype
- one scar package (failed-memory-extraction) applied conditionally from memory state
- one focal object generator (broken-halo-terminal) producing a declared write-back on the scene
- one weather system (slow-signal-dust) bound to the biome
- one companion composition mode (shrine) plus a fallback (walker)
- six animation behavior modules (`breath-offset`, `core-pulse`, `anchor-pulse`, `flow-field-drift`, `ghost-trail`, `relic-phase`)
- render synthesis pass that reads the scene graph and assigns glyph, palette role, density, and animation binding per cell
- pack registry loading for every new content class with schema validation
- full scene reproducibility from the scene equation object

Exit criteria:

- the Signal Chapel reads as reverent-instability in both `pure-text` and `rich-unicode`
- the focal object becomes the compositional center of mass without flooding the screen
- the failed-memory-extraction scar visibly shapes the chapel when the user has a recent failed memory; absent otherwise
- the companion appears in `shrine` mode inside the chapel and writes back to field values
- regeneration from the same scene equation produces the same scene
- the existing Slice 1 and Slice 2 behaviors remain intact

## Vertical Slice 4: Procedural Packs

Ship:

- installable ambient and distortion behavior packs
- additional biome packs (`archive-shaft`, `reactor-crypt`, `scar-garden`) loaded at runtime without hardcoding
- additional scar and focal packs
- optional companion entities
- unlockable portrait variants and mutation hooks
- richer capability-aware rendering for `rich-unicode`
- theme switching (palette remap) without breaking part or biome semantics

## Vertical Slice 5: Deeper Behavior

Ship:

- provider adapter abstraction in active use
- tool/action bridge with auditable events
- `building`, `researching`, `dreaming`, `recovering`, and `focused` modes
- reflective dream subsystem with guardrails
- richer companion roles tied to real subsystem responsibilities

## Vertical Slice 6: Productization

Ship:

- import/export flows
- migration strategy for memory and packs
- telemetry and diagnostics policy
- recovery and corruption handling
- packaging for multiple shell surfaces
- optional hybrid graphics adapter paths

## Major Risks

- overbuilding a framework before presence is proven
- letting random animation destroy iconic stability
- letting procedural generation outrun motion hierarchy and readability
- storing too much transcript as identity
- making dream mode sloppy or gimmicky
- letting module packs bypass system boundaries
- turning visible evolution into cosmetic clutter

## Simplifications

- start with file-backed persistence before a more complex store
- start with one portrait size and one shell layout
- start with one default theme
- start with one memory-to-artifact path
- start with one ambient profile and one distortion preset family
- start with one local provider adapter stub before multi-provider orchestration

## Minimum Implementation

To prove the new procedural direction quickly without overbuilding, implement only this:

1. capability detector with three tier outputs and conservative defaults
2. scene model builder for portrait, ambient field, event layer, and text-ui layer
3. diff-based cell redraw abstraction
4. one portrait with seeded micro-motion hooks
5. two mode profiles with visibly different ambient and eye behavior
6. one memory promotion path that unlocks one relic or scar
7. one companion entity with calm orbit logic
8. one controlled distortion preset for dream or memory resurfacing

Anything beyond this should wait until the first slice already feels emotionally convincing.

## Near-Term Next Actions

1. Implement capability detection, scene assembly, and render-state validation.
2. Implement a shell renderer that can compose the starter portrait pack into a cell grid.
3. Implement diff-based redraw for changed cells or changed regions.
4. Implement command routing for `send`, `help`, `soul`.
5. Implement profile/session persistence and the first artifact unlock from a promoted memory.
