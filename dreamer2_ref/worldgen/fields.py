"""Invisible world field seeding and propagation.

Fields live on cells (via cell.fields). Seeding is done from biome
base, focal objects, scars, and companion state. Propagation is a
simple radial falloff; this is enough to drive legible atmosphere
for the first slice.
"""

from __future__ import annotations

import math
from typing import Iterable, Tuple

from .cells import SceneGraph
from .registry import Registry
from .scene_equation import SceneEquation


def seed_base(scene: SceneGraph, equation: SceneEquation, registry: Registry) -> None:
    archetype = registry.archetypes.get(equation.biome_id)
    if archetype is None:
        return

    base_sacredness = 0.25
    base_signal = 0.15
    for row in scene.cells:
        for cell in row:
            if cell.type in ("void",):
                continue
            cell.fields["field.sacredness"] = base_sacredness
            cell.fields["field.signal"] = base_signal
            cell.fields["field.memory_resonance"] = 0.0
            cell.fields["field.damage"] = 0.0


def raise_field_radial(
    scene: SceneGraph,
    center: Tuple[int, int],
    field_id: str,
    delta: float,
    falloff: float = 0.3,
    max_radius: int = 12,
) -> None:
    cx, cy = center
    for y in range(max(0, cy - max_radius), min(scene.height, cy + max_radius + 1)):
        for x in range(max(0, cx - max_radius), min(scene.width, cx + max_radius + 1)):
            dx = x - cx
            dy = (y - cy) * 2
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > max_radius:
                continue
            t = 1.0 - (dist / max_radius)
            contribution = delta * (t ** max(falloff, 0.05))
            cell = scene.cells[y][x]
            if cell.type == "void":
                continue
            current = cell.fields.get(field_id, 0.0)
            cell.fields[field_id] = _clamp(current + contribution)


def raise_field_region(
    scene: SceneGraph,
    region_cells: Iterable[Tuple[int, int]],
    field_id: str,
    delta: float,
) -> None:
    for x, y in region_cells:
        cell = scene.cells[y][x]
        if cell.type == "void":
            continue
        current = cell.fields.get(field_id, 0.0)
        cell.fields[field_id] = _clamp(current + delta)


def _clamp(value: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))
