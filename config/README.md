# Config

This folder holds human-edited runtime configuration and profile seeds.

- `defaults/app.config.example.json`: base runtime composition and adapter slots.
- `defaults/companion.profile.example.json`: identity seed, temperament, and symbolic preferences.
- `defaults/runtime.registry.example.json`: initial load order for theme, packs, modes, and commands.

The shell config now also carries capability-tier preferences and redraw policy so the same scene model can adapt across plain text terminals, richer Unicode terminals, and optional hybrid graphics surfaces.

Treat these as examples and boot defaults, not as the only valid persistence format.
