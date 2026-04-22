# Shared Layer

Shared is not a hidden application layer. It contains neutral contracts and utilities that every layer needs.

Allowed concerns:

- canonical IDs
- event envelopes
- seeded randomness helpers
- timestamps and clocks
- schema validation
- value normalization

Forbidden concerns:

- provider-specific prompting logic
- renderer-specific layout code
- direct durable memory mutation
