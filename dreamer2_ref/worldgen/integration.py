"""Companion integration: composition mode selection and scene write-back.

Chooses a composition mode compatible with the biome, applies declared
sceneWriteBackRules, and marks the focal cell(s) as the companion's
anchor if the mode is shrine.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .cells import SceneGraph
from .fields import raise_field_radial
from .registry import Registry
from .scene_equation import SceneEquation


def place_companion(scene: SceneGraph, equation: SceneEquation, registry: Registry) -> Optional[str]:
    archetype = registry.archetypes.get(equation.biome_id)
    allowed_order = list(archetype.get("allowedCompositionModes", []) if archetype else [])
    allowed_set = set(allowed_order)

    mode_id = equation.composition_mode_id
    mode = _resolve_mode(registry, mode_id, allowed_order, allowed_set)

    if mode is None:
        return None

    scene.companion_mode_id = mode["id"]

    # Write-back: raise sacredness and signal near focal or agent.
    if scene.focal_cell is None:
        return mode["id"]

    cx, cy = scene.focal_cell
    for rule in mode.get("sceneWriteBackRules", []):
        kind = rule.get("effect")
        field_id = rule.get("fieldId")
        delta = float(rule.get("delta", 0.0))
        if kind == "raise-field" and field_id:
            raise_field_radial(scene, (cx, cy), field_id, delta, falloff=0.3, max_radius=8)

    return mode["id"]


def _resolve_mode(
    registry: Registry,
    preferred_id: Optional[str],
    allowed_order: list,
    allowed_set: set,
) -> Optional[Dict[str, Any]]:
    visited: set = set()
    candidate_id = preferred_id

    while candidate_id and candidate_id not in visited:
        visited.add(candidate_id)
        mode = registry.composition_modes.get(candidate_id)
        if mode is None:
            # preferred or chained fallback missing from registry; stop the
            # chain and fall through to the biome's allowed list.
            break
        if not allowed_set or candidate_id in allowed_set:
            return mode
        candidate_id = mode.get("fallbackModeId")

    # Preferred unavailable or not allowed; pick the first allowed mode
    # present in the registry, preserving the archetype's declared order.
    for mode_id in allowed_order:
        if mode_id == preferred_id:
            continue
        mode = registry.composition_modes.get(mode_id)
        if mode is not None:
            return mode
    return None
