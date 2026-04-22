"""Focal object installation and scene write-back.

Installs the focal object at the scene's compositional center of mass,
applies declared sceneWriteBack effects (raise-field, halo-bloom, etc.),
and tags focal cells with dominant motif and active state.
"""

from __future__ import annotations

from .cells import SceneGraph
from .fields import raise_field_radial
from .registry import Registry
from .scene_equation import SceneEquation


def install(scene: SceneGraph, equation: SceneEquation, registry: Registry) -> None:
    focal = registry.focals.get(equation.focal_object_id)
    if focal is None:
        return

    cx, cy = scene.width // 2, scene.height // 2
    scene.focal_cell = (cx, cy)

    # The focal occupies a small 3-wide "altar" motif at the center.
    half = 1
    for dy in range(-half, half + 1):
        for dx in range(-(half + 1), half + 2):
            x, y = cx + dx, cy + dy
            if not scene.in_bounds(x, y):
                continue
            cell = scene.cell_at(x, y)
            if cell.type == "void":
                continue
            cell.type = "altar"
            cell.active_state = "ritual-active"
            cell.motif_tag = focal.get("dominantMotif")
            cell.glyph_family = "structural"
            cell.palette_role = "energy_or_event"
            if dx == 0 and dy == 0:
                cell.glyph_family = "symbolic"
                cell.palette_role = "rare_anomaly"

    # Apply scene write-back effects.
    for effect in focal.get("sceneWriteBack", []):
        kind = effect.get("effect")
        field_id = effect.get("fieldId")
        delta = float(effect.get("delta", 0.0))
        falloff = float(effect.get("falloff", 0.3))
        if kind in ("raise-field", "halo-bloom") and field_id:
            raise_field_radial(scene, (cx, cy), field_id, delta, falloff=falloff, max_radius=12)
