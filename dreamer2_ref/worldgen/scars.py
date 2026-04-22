"""Scar package application.

Scars are conditional; activationRules.requiresMemoryTag must match
one of the provided memory tags for the scar to apply. When applied,
scars modify fields, material assignments, and motif bias in the
focal ring and a traffic lane.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .cells import SceneGraph
from .fields import raise_field_radial, raise_field_region
from .registry import Registry
from .scene_equation import SceneEquation


def apply(
    scene: SceneGraph,
    equation: SceneEquation,
    registry: Registry,
    memory_tags: Iterable[str],
) -> list[str]:
    applied: list[str] = []
    memory_tag_set = set(memory_tags or ())

    for scar_id in equation.scar_ids:
        scar = registry.scars.get(scar_id)
        if scar is None:
            continue
        if not _should_apply(scar, memory_tag_set):
            continue
        _apply_scar(scene, scar, equation)
        applied.append(scar_id)

    scene.applied_scars = applied
    return applied


def _should_apply(scar: dict[str, Any], memory_tags: set) -> bool:
    rules = scar.get("activationRules") or {}
    conditional_on = rules.get("conditionalOn")
    if conditional_on is None:
        return True
    if conditional_on == "memory-state":
        required = rules.get("requiresMemoryTag")
        if required is None:
            return True
        return required in memory_tags
    # Other activation rule kinds default to unconditional for Slice 3.
    return True


def _apply_scar(scene: SceneGraph, scar: dict[str, Any], equation: SceneEquation) -> None:
    if scene.focal_cell is None:
        return

    cx, cy = scene.focal_cell

    # Field effects on the focal ring and a traffic lane.
    for effect in scar.get("fieldEffects", []):
        field_id = effect.get("field")
        delta = float(effect.get("delta", 0.0))
        falloff = float(effect.get("falloff", 0.3))
        region = effect.get("region", "focal")
        if field_id is None:
            continue

        if region == "focal":
            raise_field_radial(scene, (cx, cy), field_id, delta, falloff=falloff, max_radius=4)
        elif region == "focal-ring":
            raise_field_radial(scene, (cx, cy), field_id, delta, falloff=falloff, max_radius=8)
        elif region == "traffic-lane":
            lane_cells = _traffic_lane_cells(scene)
            raise_field_region(scene, lane_cells, field_id, delta)

    # Topology effects: seams at the focal edge.
    for effect in scar.get("topologyEffects", []):
        kind = effect.get("effect")
        if kind == "seam-open-at-focal-edge":
            _mark_seam_ring(scene, cx, cy, intensity=float(effect.get("intensity", 0.3)))
        elif kind == "stitched-repair-trace":
            _mark_traffic_lane_seam(scene, float(effect.get("intensity", 0.3)))

    # Motif bias: carry the seam-stitch motif onto affected cells.
    for bias in scar.get("motifBias", []):
        motif_id = bias.get("motif")
        if motif_id is None:
            continue
        _stamp_motif_on_damaged_cells(scene, motif_id)


def _traffic_lane_cells(scene: SceneGraph) -> list[tuple[int, int]]:
    # A simple traffic lane along the mid-row entering from the left.
    y = scene.height // 2
    return [(x, y) for x in range(1, scene.width // 2 - 1) if scene.in_bounds(x, y)]


def _mark_seam_ring(scene: SceneGraph, cx: int, cy: int, *, intensity: float) -> None:
    import math

    radius = 6
    for y in range(max(0, cy - radius), min(scene.height, cy + radius + 1)):
        for x in range(max(0, cx - radius), min(scene.width, cx + radius + 1)):
            dx = x - cx
            dy = (y - cy) * 2
            dist = math.sqrt(dx * dx + dy * dy)
            if radius - 0.8 <= dist <= radius + 0.2:
                cell = scene.cell_at(x, y)
                if cell.type == "void":
                    continue
                cell.active_state = "scarred"
                if "scar.failed-memory-extraction" not in cell.dominant_influences:
                    cell.dominant_influences.append("scar.failed-memory-extraction")


def _mark_traffic_lane_seam(scene: SceneGraph, intensity: float) -> None:
    y = scene.height // 2
    for x in range(1, scene.width // 2 - 1):
        if not scene.in_bounds(x, y):
            continue
        cell = scene.cell_at(x, y)
        if cell.type == "void":
            continue
        if cell.type == "floor":
            cell.active_state = "scarred"
            cell.motif_tag = "motif.seam-stitch"
            cell.dominant_influences.append("scar.failed-memory-extraction")


def _stamp_motif_on_damaged_cells(scene: SceneGraph, motif_id: str) -> None:
    for row in scene.cells:
        for cell in row:
            if cell.active_state == "scarred" and cell.motif_tag is None:
                cell.motif_tag = motif_id
