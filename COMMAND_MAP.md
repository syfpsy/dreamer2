# Command Map

Commands are subsystem entry points, not roleplay flavor.

## Grammar

`command [subject] [flags] [payload]`

Commands should be parseable in a minimal shell, but also invocable by shortcuts, panels, or future UI surfaces.

## Core Domains

### `send`

Primary transmission channel.

Examples:

- `send Draft a release note from today's changes`
- `send --mode building Refactor the memory scorer`

Subsystems:

- conversation dispatch
- tool routing
- task execution
- transcript logging

### `help`

Discovers commands, directives, module affordances, and current mode limitations.

### `soul`

Identity and visible-state inspection.

Examples:

- `soul`
- `soul portrait`
- `soul seed`
- `soul scars`

Subsystems:

- identity profile
- portrait anatomy
- current symbolic state
- seed and evolution inspection

### `memory`

Memory and ledger inspection.

Examples:

- `memory recent`
- `memory durable`
- `memory artifact archive-lantern`

Subsystems:

- raw history query
- curated memory ledger
- visible artifacts
- correction entry points

Current reference-runtime behavior:

- `memory` selects the latest durable record and lifts the left-side surface into detailed memory inspection
- `memory <id>` selects a specific durable memory
- `memory next` and `memory prev` rotate through durable memory selection

### `dream`

Controlled reflection and synthesis.

Examples:

- `dream reflect recent session`
- `dream surface unresolved threads`

Rules:

- no uncontrolled nonsense mode
- output is flagged as reflective unless promoted
- distortion profile may change during dream ingress/egress

### `essence`

Configuration and personality tuning without breaking continuity.

Examples:

- `essence show`
- `essence theme sacred-machine-default`
- `essence ambient low`

### `gallery`

Evolution history, snapshots, milestones, and symbolic timeline browsing.

Current reference-runtime behavior:

- writes a concise gallery audit into the transmission log
- lifts the left-side surface into `gallery` focus until another surface command replaces it
- shows artifact bindings back to source memory IDs
- supports `gallery next`, `gallery prev`, artifact IDs, and numeric selection for lightweight browsing

### `forget`

Correction and pruning workflow.

Examples:

- `forget memory mem_019`
- `forget preference midnight-theme`

Rules:

- destructive forget operations require confirmation based on policy
- symbolic artifacts must declare whether they dissolve, archive, or scar

### `tweak`

Cosmetics, modules, panels, and optional pack toggles.

### `mode`

Explicit mode change request when automatic inference is not enough.

Examples:

- `mode listening`
- `mode focused`

## Command Design Rules

- Every command must map to a handler reference.
- Every command must declare affected layers.
- Every command must define mode availability.
- Help text must reflect actual loaded modules, not static fiction.
