# Companion Organism

## Purpose

The companion is not an ASCII sprite. It is a procedurally evolving identity organism composed from lineage, DNA, mode, memory, scars, relics, satellites, and the place it currently stands in. It inherits the scene's glyph families, palette roles, motifs, and materials and contributes back its own motion, posture, and symbolic marks.

This document defines identity DNA, composition modes, companion objects, lineage, and mutation rules. Portrait anatomy lives in `PORTRAIT_SPEC.md` and remains authoritative for slot mechanics. This doc layers identity organism logic above those slots.

## Identity DNA

Each companion is defined by a DNA record that is the seed for every render. DNA is authored once per profile and then evolves only through declared vectors.

DNA fields:

- `id`, `label`, `lineage_id`
- `seed`: stable string or integer
- `archetype_bias`: weights across companion archetypes (watcher, archivist, ritualist, courier, repairer, dreamer, sentinel, scribe, organist)
- `silhouette_intent`: quiet, imposing, fragile, coiled, ceremonial, vigilant
- `glyph_family_bias`: weights across structural, soft-signal, dense-pressure, decay, symbolic
- `motif_set`: companion-side motifs (orbiting sigil, halo ring, vow mark, stitched seam, data rivet, lantern drop, prayer bracket)
- `palette_roles`: references into the palette doctrine
- `material_affinity`: which world materials the companion resonates with
- `preferred_composition_modes`: ordered preference list (shrine, walker, projection, embedded, remote-presence)
- `motion_personality`: blink cadence, drift bias, breath depth, orbit style, pulse temperament
- `scar_style`: stitched, ember, dusted, vow, sealed, quiet
- `evolution_permissions`: which evolution vectors are allowed
- `inheritance_policy`: which fields a lineage child may inherit or reroll

DNA is storage, not a portrait. A portrait is synthesized from DNA plus the current scene, mode, memory state, and visible artifacts.

## Lineages

A lineage is a family of companions that share motifs, silhouette intent, palette discipline, and evolutionary constraints. A lineage is declarative and packaged under `packs/companions/lineages/`. Different users may meet different companions, but companions in the same lineage feel like relatives.

Starter lineages:

- `lineage.quiet-archivists`: soft-signal biased, vow marks, lantern motifs
- `lineage.signal-wardens`: structural biased, halo rings, watchtower posture
- `lineage.stitched-menders`: decay-aware, scar-proud, stitched seams
- `lineage.ritual-sentinels`: symbolic-biased, containment-clasp motifs
- `lineage.dream-scribes`: dream-soft distortion affinity, orbiting sigils
- `lineage.relay-couriers`: directional-drift affinity, cable-rivet motifs
- `lineage.choir-organists`: chanting cadence, prayer-bracket motifs

Lineage only constrains; it does not script dialogue. Voice lives in `config/companion.profile.json` and in the provider prompt assembly (`dreamer2_ref/providers.py`).

## Composition Modes

A companion exists in the scene through a composition mode. The scene equation selects a mode compatible with the place, focal, biome, and companion DNA.

Modes:

- `shrine`: the companion sits centered as the focal altar; the scene orients around it; motion is ceremonial
- `walker`: the companion is a placed agent within the topology; the world surrounds it; motion is small-body motion
- `projection`: the companion appears as a projected halo or holographic presence on a focal surface; less material, more signal
- `embedded`: the companion is partially integrated into architecture (a shrine engine, a relay pylon); only certain slots animate
- `remote-presence`: the companion speaks through the place rather than being visible; atmosphere and focal carry the conversation

Each mode declares:

- `slot_visibility`: which portrait slots are active
- `motion_multipliers`: per region
- `palette_bias`: which palette roles dominate for the agent
- `glyph_family_bias`: per mode adjustments
- `scene_write_back_rules`: how the mode alters scene behaviors (e.g., `projection` amplifies signal field lines toward the focal)
- `compatible_biomes`
- `fallback_mode`: graceful fallback if the scene cannot support this mode

Composition modes are first-class content and ship under `packs/companions/composition-modes/`.

## Companion Objects

Satellites are first-class. They are not pets and not decoration. They are meaning-bearing objects tied to specific system state and to lineage vocabulary.

Companion object types:

- `signal-bird`: small directional drifter, scans for incoming transmissions
- `archive-shard`: slow orbital, lights near memory_resonance
- `relic-drone`: symbolic, appears during artifact reveals
- `stitched-ember`: hot pinpoint, warms during recovery
- `vow-ring`: orbits at a vow cadence, commemorates a kept promise
- `lantern-drop`: descends slowly, marks dream exits
- `prayer-bracket`: flanks the agent during ritual-active states

Each object declares: slot, glyph family, motion behavior module references, narrative meaning, source memory binding, and appearance rules. Objects persist across scenes if their source state persists; they fade cleanly when their source state dissolves.

## Mutation And Evolution

The silhouette changes last, not first. Evolution accrues in small visible truths:

- `scar`: earned by a recovered strain event
- `relic`: earned by a preserved or commemorated memory
- `halo-refinement`: earned by trust or continuity milestones
- `core-adornment`: earned by sustained building or craft
- `sigil`: earned by a recurring shared motif in user memories
- `companion-object-unlock`: earned by a declared milestone

Disallowed without explicit arc:

- full silhouette replacement
- constant whole-face mutation
- noisy independent motion on every slot

Every evolution must declare its source memory or milestone and must be inspectable through `soul`, `memory`, and `gallery`.

## Mode-Dependent Behavior

A companion cycles through system modes (standby, listening, thinking, building, researching, dreaming, recovering, focused). Modes do not replace identity. They modulate motion intensity, signal density, distortion permission, and slot emphasis.

Mode bindings:

- `standby`: minimum motion; eye flicker permitted; soft-signal drift only
- `listening`: relay points; attentive eye; small directional drift toward speaker
- `thinking`: dense pressure pulses in core; no whole-body animation
- `building`: jaw tension; tool sigil may warm; focused scan
- `researching`: quiet core; lantern drop active; small halo scan
- `dreaming`: softened alignment; dream-soft distortion permitted; halo haze
- `recovering`: scar layer warms; stitched seams active; cautious motion
- `focused`: steady core pulse; minimum ambient interference

## Scene Integration Contract

When the scene composition pass places the companion, it must:

- select a composition mode compatible with the scene equation
- apply `scene_write_back_rules` so the world reacts to the agent
- bind slot behavior to animation registry modules
- ensure palette roles are shared with the scene, not inherited from a different palette
- enforce the silence ratio of the biome; the companion does not increase density beyond budget
- respect the capability tier; slots degrade before the identity breaks

## Graceful Degradation

Across capability tiers, the companion must preserve:

- silhouette
- one eye or core signal
- one active scar or relic if present
- mode legibility
- companion object presence if it belongs to the scene

Tiers enrich, but the identity organism survives in `pure-text`.

## What This Is Not

- Not a text-emoji avatar.
- Not a sprite.
- Not a roleplay persona fork.
- Not a chatbot portrait sticker.

It is a procedural identity organism that shares the place's glyphs, palette, motifs, and motion budget, carries user memory as visible truth, and evolves through declared, inspectable arcs.
