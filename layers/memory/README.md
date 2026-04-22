# Memory Layer

Owns durable continuity.

Responsibilities:

- store raw events
- maintain curated memory ledgers
- generate and update artifacts
- manage visible evolution state
- support inspect, revise, forget, and export flows

Inputs:

- session events
- memory candidates
- promotion rules
- artifact and evolution registries

Outputs:

- ledger entries
- artifact deltas
- visible evolution state
- exportable records

The memory layer should be durable, inspectable, and reversible wherever possible.
