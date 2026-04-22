"""Atmospheric pass: ambient fields and weather seeding.

Populates micro-detail near meaning (focal, scars, agent) using the
biome's silence ratio as a density cap. Weather systems claim their
own density budget and bias their dominant axis through the scene.
"""

from __future__ import annotations

from typing import Any, Dict

from .cells import SceneGraph
from .registry import Registry
from .scene_equation import SceneEquation
from .streams import stream


def apply(scene: SceneGraph, equation: SceneEquation, registry: Registry) -> None:
    archetype = registry.archetypes.get(equation.biome_id)
    if archetype is None:
        return

    silence = float(archetype.get("silenceToDetailRatio", 0.7))

    if equation.weather_id:
        weather = registry.weather.get(equation.weather_id)
        if weather:
            _apply_weather(scene, weather, silence, equation)


def _apply_weather(scene: SceneGraph, weather: Dict[str, Any], silence: float, equation: SceneEquation) -> None:
    dominant_axis = weather.get("dominantAxis", "horizontal")
    density_budget = weather.get("densityBudget", {})
    absolute_cap = float(density_budget.get("absoluteCap", 0.08))
    # Convert absolute cap under the biome's silence regime.
    effective_density = max(0.0, absolute_cap * (1.0 - silence * 0.5))

    rng = stream(equation.seed, f"weather.{weather['id']}")

    cx = scene.width // 2
    cy = scene.height // 2

    for y in range(scene.height):
        for x in range(scene.width):
            cell = scene.cell_at(x, y)
            if cell.type not in ("floor", "void"):
                continue

            # Weather biases follow the dominant axis.
            if dominant_axis == "horizontal":
                axis_bias = 1.0 - abs((y - cy) / max(1, scene.height // 2))
            elif dominant_axis == "vertical":
                axis_bias = 1.0 - abs((x - cx) / max(1, scene.width // 2))
            else:
                axis_bias = 0.6

            signal = cell.fields.get("field.signal", 0.0)
            # Weather aligns toward focal halo (amplify near focal).
            focal_bias = 0.5 + 0.5 * signal

            if rng.random() < effective_density * axis_bias * focal_bias:
                if cell.type == "void":
                    cell.active_state = "humming"
                else:
                    cell.active_state = "humming"
                if cell.glyph_family not in ("soft-signal", "symbolic"):
                    cell.glyph_family = "soft-signal"
                if cell.palette_role in ("structural",):
                    cell.palette_role = "energy_or_event"
                cell.motion_tag = weather.get("animationBinding", "behavior.flow-field-drift")
