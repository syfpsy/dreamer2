# Memory Model

## Core Principle

Raw history is not the same thing as durable memory.

The system stores both:

- `event history`: everything that happened
- `curated memory`: what deserves continuity

Those stores must remain separate so the companion can remember meaningfully without turning every transcript into permanent identity.

## Memory Categories

### Active Session Memory

- current conversational state
- short-lived task context
- pending references
- expires or compresses aggressively

### Long-Term Personal Memory

- stable preferences
- biography fragments
- recurring dislikes
- values, rituals, cadence preferences

### Project And Task Memory

- goals
- ongoing projects
- build decisions
- active constraints
- recurring workflows

### Relationship Or Narrative Memory

- shared milestones
- vows
- conflict and repair arcs
- emotional tone patterns
- symbols with interpersonal meaning

### World Or System Memory

- module state
- environment facts
- tool availability
- shell history
- implementation decisions

### Cosmetic Or State Memory

- unlocked portrait parts
- scars
- relic ownership
- preferred theme
- ambient field biases
- gallery history

## Memory Lifecycle

1. raw event is stored
2. mind proposes memory candidates
3. memory manager scores candidates
4. candidate is rejected, deferred, or promoted
5. promoted memory may create or modify artifacts
6. visible evolution state is updated

## Promotion Heuristics

Promote when one or more are true:

- explicit user correction or preference statement
- repeated recurrence across sessions
- active project relevance
- emotional or symbolic weight
- milestone completion
- failure followed by recovery

Do not promote:

- transient filler
- sensitive content without a clear retention basis
- one-off speculative ideas with no reuse signal
- high-noise outputs from dream or reflection paths unless confirmed

## Editability And Forgetting

Every durable memory must declare:

- `owner`: user, system, or shared
- `editability`: locked, guided, or free-edit
- `forgetPolicy`: pruneable, confirm-required, or permanent-until-exported
- `visibility`: hidden, inspectable, shell-visible, or symbolic

Correction flow:

1. inspect memory
2. mark incorrect or outdated
3. choose revise, retire, or forget
4. update downstream artifacts if necessary

## Symbolic Memory Outputs

Memory may surface as:

- relics
- scars
- archive cards
- timeline markers
- orbiting fragments
- gallery snapshots
- stitched repairs

Every symbolic object should include source memory IDs and a reversible display rule.

## Memory-To-Visual Mapping

Visible continuity is not a side effect. It is an explicit output of the memory layer.

Promotion into symbolic rendering should flow through a dedicated mapping step:

1. durable memory is promoted or revised
2. memory-to-symbol mapper evaluates eligibility
3. mapper selects symbolic consequence classes
4. artifact manager creates or updates visible state
5. shell receives renderable deltas, not raw memory internals

Eligible memory-to-visual outcomes include:

- long-lived preferences -> panel tone shifts, glyph-family bias, shell accent preferences
- important shared milestones -> relics, halo marks, gallery snapshots, timeline markers
- repeated project themes -> archive cards, orbiting shards, tool sigils
- repaired misunderstandings -> stitched seams, scars, or repair marks
- persistent goals -> orbiting guide objects, vow marks, or status sigils
- identity events -> core marks, halo refinements, companion unlocks

Starter runtime examples already implemented:

- preference statements -> archive lantern relic unlock
- recovery language -> stitched echo scar
- project commitments -> builder mark plus workshop snapshot in the shelf and gallery
- shared vows or milestones -> orbit fragment with archive-shard accompaniment

## Symbol Promotion Rules

A memory should become visible symbolism only if it is:

- durable enough to survive session churn
- meaningful enough to justify shell real estate
- reversible or inspectable
- legible within the current motion and glitch budget

The shell should render continuity, not only report it. Raw storage remains separate from symbolic consequence.

## Visual Consequence Constraints

- one memory may produce multiple symbolic effects, but only through declared artifact rules
- symbolic state must be inspectable back to source memory IDs
- forgetting or revising memory must update downstream symbolic state
- dream outputs should not create permanent symbols unless confirmed or re-encountered

## Memory Echoes In The World

Memory does not only surface on the companion. Recurring or durable memories can echo in the place itself as environmental motifs, dormant symbols, stitched seams, or a raised `memory_resonance` field value. See `WORLD_GENERATION.md` for the field semantics and `PLACE_GRAMMAR.md` for motif integration.

Echo rules:

- an echo must trace back to a source memory id
- an echo must never violate the biome's silence ratio or palette doctrine
- an echo appears as motif bias, field seed, dormant symbol placement, or scar-echo at reduced intensity
- forgetting or revising the source memory must update or dissolve the echo
- echoes are inspectable via `inspect scene` and `inspect cell` (future)

A memory-to-world echo mapper runs alongside the existing memory-to-symbol mapper. They are sibling mappers operating on the same promotion output.

## Export And Portability

Support export at four levels:

- raw session history
- durable memory ledger
- artifact gallery
- profile and cosmetic state

Portability matters because the system is intended to outlive any one model provider or renderer.
