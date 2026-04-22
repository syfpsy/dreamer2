# Procedural Animation

## Core Doctrine

The shell is a capability-aware procedural cell-rendering engine. It should feel alive through sparse controlled movement, not through obvious looping ASCII GIF behavior.

The source of truth is the scene model. A renderer may target text cells, richer Unicode grids, or optional hybrid graphics, but the artistic logic must survive renderer changes.

## Capability Tiers

### Pure Text

- ANSI styling only
- narrow character assumptions
- conservative redraw strategy
- structural identity and motion hierarchy must still read clearly

### Rich Unicode

- wider glyph inventory
- denser texture options
- more expressive symbolic marks
- better color depth when available

### Hybrid Graphics

- optional cinematic transitions
- image-like overlays or richer compositing
- advanced graphics protocols or web/canvas shell surfaces

The engine must never require this tier to feel complete.

## Glyph Families

### Structural

Examples: `| / \ _ - [ ] ( ) < >`

Function:

- stable body form
- frame geometry
- terminal architecture
- high-persistence silhouette

### Soft Signal

Examples: `. , ' : ~`

Function:

- breath
- haze
- calm field drift
- low-energy shell life

### Dense Pressure

Examples: `# % @ = +`

Function:

- thinking load
- focused processing
- pressure around core or visor

### Decay

Examples: `; ^ x ! ?`

Function:

- dream residue
- instability
- corruption or repair traces

### Symbolic

Examples: `* + o O`

Function:

- relics
- vows
- soul-state emphasis
- unlock and ritual marks

The renderer should animate and substitute within family constraints first. It should not treat all glyphs as interchangeable.

## Motion Hierarchy

- portrait center: most stable
- portrait edges: small approved motion
- ambient field: sparse low-energy drift
- companion objects: visible but restrained motion
- panels and borders: calmer than field
- command area: highest readability priority, lowest visual interference

Most of the screen should remain stable most of the time.

## Timing Doctrine

- use very small changes per frame
- prefer temporal dithering over brute-force redraw
- avoid synchronizing all regions
- use variable timing windows to prevent obvious loops
- reserve large effects for meaningful events only

Suggested early cadence targets:

- shell frame cadence: `80-160ms`
- ambient updates: `400-3000ms` depending on region
- rare events: short bursts under `1200ms`
- dream drift: slow and non-uniform

## Controlled Randomness Categories

### Seeded Identity Randomness

Stable per-profile visual DNA:

- blink personality
- contour asymmetry
- ornament density
- preferred noise family
- relic orbit style
- drift bias

### State-Based Randomness

Changes with active mode:

- density
- softness
- distortion allowance
- motion intensity
- field directionality

### Region-Based Randomness

Different shell regions behave differently:

- portrait core
- portrait edges
- empty field
- borders
- command area
- memory surfaces

### Time-Based Randomness

Avoids visible loops through:

- slow phase shifts
- variable windows
- rare event chances
- staggered per-region cadence

## Render Passes

1. core silhouette
2. ambient field
3. state overlays
4. event overlays
5. text and UI surfaces

Portrait-specific subpasses can still resolve head, eyes, core, halo, scars, relics, and companions internally.

## Ambient Field Behaviors

The ambient field is a real subsystem. It should support:

- signal dust
- punctuation drift
- coordinate ticks
- dormant symbols
- faint scan residue
- directional field movement

State tendencies:

- `standby`: sparse and calm
- `listening`: attentive relay points and light pulse
- `thinking`: denser, more directional, but still bounded
- `dreaming`: looser geometry, residue, and softened rules
- `recovering`: stitched, cautious, reorganizing

Never allow a full-screen snowstorm.

## Distortion Rules

Distortion is ceremonial and rare. Allowed uses:

- wake
- dream entry or exit
- severe strain
- unlock
- memory resurfacing
- symbolic reveal

Profiles may include:

- resolve from noise
- brief desynchronization
- soft phase-in
- readable ghost-trail

Glitch budget rules:

- most sessions remain mostly stable
- do not stack distortions casually
- readability always outranks spectacle

## Procedural Simulation Hooks

Optional pluggable behavior families:

- flow-field movement for dust, orbiting fragments, and signal drift
- cellular spread for corruption, healing, or memory resurfacing
- constraint-based portrait mutation for emotional and long-term change
- swarm logic for companion entities or archive fragments
- reaction-diffusion-like bloom for dream halos or sacred atmosphere

These are behavior classes, not hardcoded mandates.

## Memory-To-Visual Mapping

Eligible durable memories may become:

- relics
- scars
- sigils
- halo marks
- orbiting objects
- stitched seams
- gallery snapshots

Examples:

- long-lived preference -> panel or glyph bias
- shared milestone -> relic or sigil
- repaired misunderstanding -> stitched seam or scar
- persistent goal -> orbiting guide object
- repeated project theme -> archive card or halo mark

Promotion into symbolism must remain separate from raw storage.

## Minimum Proof

The first convincing implementation only needs:

- one stable iconic portrait
- one seeded identity profile
- one ambient field behavior
- two visibly different calm modes
- one symbolic memory artifact
- one orbiting relic or companion
- a diff-based redraw abstraction

Anything beyond that should justify itself against clarity, continuity, and recognizability.
