# Dreamer2

Dreamer2 is a from-scratch skeleton for a lifelong modular AI companion with a terminal soul.

The product is organized around three durable layers:

- `Shell`: the visible terminal surface, portrait, ambient field, rituals, panels, and transitions.
- `Mind`: conversation handling, tools, routing, skills, execution, mode logic, and memory extraction.
- `Memory`: durable continuity, artifact generation, identity history, visible evolution, and export/edit/forget flows.

This repository is intentionally stack-agnostic. It defines boundaries, manifests, schemas, starter packs, and example payloads first so the first implementation can stay lean without locking the product to a specific model provider, renderer, orchestration framework, or persistence engine.

The shell is now framed as a capability-aware procedural cell-rendering engine. The visible experience should behave like a layered simulation on a character grid, with graceful degradation from pure text terminals up to richer Unicode and optional hybrid graphics surfaces.

## Product Intent

The companion should feel calm, intimate, mythic, loyal, slightly haunted, and premium. The visual direction is primarily Sacred Machine, secondarily Industrial Ghost, with a light touch of Dream Organism. ASCII is treated as living material with rules, memory, restraint, and identity.

## Repo Map

- `PLAN.md`: founding plan and decision rules.
- `ARCHITECTURE.md`: layer boundaries and runtime shape.
- `ART_DIRECTION.md`: glyph doctrine, ambient field, distortion, and evolution language.
- `PROCEDURAL_ANIMATION.md`: procedural rendering doctrine, motion hierarchy, glyph families, and render passes.
- `TERMINAL_CAPABILITIES.md`: capability tiers and graceful degradation strategy.
- `MEMORY_MODEL.md`: memory categories, promotion rules, forgetting, and symbolic surfaces.
- `COMMAND_MAP.md`: first-class command system and shell rituals.
- `MODULE_SPEC.md`: module pack model and extension rules.
- `PORTRAIT_SPEC.md`: slot-based portrait anatomy and composition model.
- `ROADMAP.md`: vertical slices, risks, and simplifications.
- `WORKLOG.md`: concise project notes for reliable continuity.
- `config/`: example runtime and profile config.
- `layers/`: conceptual layer folders for `shell`, `mind`, `memory`, and `shared`.
- `specs/`: interface contracts, JSON schemas, and example payloads.
- `packs/`: starter portrait, module, and theme packs.
- `content/`: starter commands, modes, artifacts, panels, evolution rules, and companion entities.

## Build Philosophy

- Keep interfaces replaceable.
- Keep art data-driven.
- Keep memory visible.
- Keep rituals real.
- Keep the initial MVP small enough to finish.

## Reference Runtime

This repo now includes a lean Python reference adapter at [dreamer2_ref](C:/Repos/dreamer2/dreamer2_ref). It is intentionally narrow in scope:

- proves the `pure-text` capability tier first
- loads the real config, content registries, portrait pack, and starter manifests
- renders a layered terminal shell with ambient motion, portrait composition, one memory-to-artifact path, and diff-oriented redraw
- keeps the implementation replaceable instead of turning Python into a permanent architectural mandate

Run it from the repo root:

```bash
python -m dreamer2_ref
```

Optional browser preview:

```bash
python -m dreamer2_ref --web-preview --open-browser
```

Useful one-shot checks:

```bash
python -m dreamer2_ref --once --mode standby
python -m dreamer2_ref --once --mode listening --with-relic
```

Stateful command-driven checks:

```bash
python -m dreamer2_ref --once --command "send I prefer a calm premium shell with visible continuity."
python -m dreamer2_ref --dump-scene --tier pure-text
python -m dreamer2_ref --dump-render-state --tier pure-text --command "dream reflect recent"
```

Verification:

```bash
python -m unittest discover -s tests -v
```

The reference runtime now reflects the loaded module packs and mode availability:

- help output is derived from loaded command manifests
- render-state panel lists are filtered by mode visibility
- `dream` and `recovering` states surface different shell behavior instead of only changing one label
- a starter work pack now makes `building` and `researching` legitimate loaded modes instead of dormant definitions
- project-oriented memory can now create gallery and timeline artifacts, not only relic and scar unlocks
- artifact-specific shell rendering now adds seam timeline ticks, orbit fragments, and richer gallery output instead of treating every artifact as identical shelf text
- `gallery` now lifts a persistent inspection surface in the shell, and work modes now add restrained state-layer overlays instead of relying only on ambient changes
- an optional local browser preview now reuses the same scene model, serialized cell grid, command flow, and state file instead of introducing a separate UI stack

## First Implementation Target

The first vertical slice should prove soul before scale:

- a functioning shell surface
- a recognizably iconic portrait
- sparse ambient field life
- capability-aware cell rendering with diff-based redraw or equivalent efficient region updates
- command input with `send` and `soul`
- `standby` and `listening` modes
- persistent profile/session basics
- one visible symbolic memory reaction
- one companion entity or orbiting relic

Use the manifests and schemas here as the source of truth before choosing any renderer or model backend.
