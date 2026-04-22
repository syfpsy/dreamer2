# Mind Layer

Owns behavior, routing, and execution.

Responsibilities:

- parse and route commands
- select modes or request mode transitions
- adapt model/provider access
- invoke tools and actions
- extract memory candidates

Inputs:

- shell events
- profile state
- visible memory context
- module registries

Outputs:

- transmissions
- mode transition requests
- memory candidates
- task and tool events

The mind should be replaceable at the provider and orchestration boundary without changing shell or memory contracts.
