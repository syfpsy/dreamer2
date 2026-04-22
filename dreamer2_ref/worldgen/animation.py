"""Animation binder.

Enumerates scene elements with motion tags, fetches behavior modules
from the registry, validates compatibility, and records bindings on
the scene graph. Degrades gracefully by substituting the fallback
behavior when a module is incompatible with the biome or tier.
"""

from __future__ import annotations

from typing import Dict, Optional

from .cells import AnimationBinding, SceneGraph
from .registry import Registry
from .scene_equation import SceneEquation


def bind(scene: SceneGraph, equation: SceneEquation, registry: Registry, *, tier: str = "pure-text") -> None:
    # Bind behaviors carried by cells via motion_tag.
    for y, row in enumerate(scene.cells):
        for x, cell in enumerate(row):
            if cell.motion_tag is None:
                continue
            behavior = _resolve_behavior(registry, cell.motion_tag, equation.biome_id)
            if behavior is None:
                continue
            scene.bindings.append(
                AnimationBinding(
                    target="cell",
                    behavior_id=behavior["id"],
                    cell_xy=(x, y),
                    region="ambient",
                    budget_cost=behavior.get("motionBudgetCost", "low"),
                )
            )

    # Bind focal-object local behaviors if a focal cell exists.
    if scene.focal_cell is not None:
        focal = registry.focals.get(equation.focal_object_id)
        if focal is not None:
            for behavior_id in focal.get("localBehaviors", []):
                behavior = _resolve_behavior(registry, behavior_id, equation.biome_id)
                if behavior is None:
                    continue
                scene.bindings.append(
                    AnimationBinding(
                        target="focal",
                        behavior_id=behavior["id"],
                        cell_xy=scene.focal_cell,
                        region="focal",
                        budget_cost=behavior.get("motionBudgetCost", "low"),
                    )
                )

    # Bind scar-driven behaviors on scarred cells.
    for y, row in enumerate(scene.cells):
        for x, cell in enumerate(row):
            if cell.active_state != "scarred":
                continue
            scar_bindings = _scar_bindings_for_cell(registry, scene.applied_scars, equation.biome_id)
            for behavior_id in scar_bindings:
                scene.bindings.append(
                    AnimationBinding(
                        target="scar",
                        behavior_id=behavior_id,
                        cell_xy=(x, y),
                        region="scar",
                        budget_cost="medium",
                    )
                )


def _resolve_behavior(
    registry: Registry,
    behavior_id: str,
    biome_id: str,
) -> Optional[Dict]:
    visited: set = set()
    candidate_id = behavior_id

    while candidate_id and candidate_id not in visited:
        visited.add(candidate_id)
        behavior = registry.behaviors.get(candidate_id)
        if behavior is None:
            return None
        compatible = behavior.get("compatibleBiomes") or ["*"]
        if "*" in compatible or biome_id in compatible:
            return behavior
        candidate_id = behavior.get("fallbackBehaviorId")
    return None


def _scar_bindings_for_cell(registry: Registry, applied_scars, biome_id: str):
    bindings = []
    for scar_id in applied_scars:
        scar = registry.scars.get(scar_id)
        if scar is None:
            continue
        for behavior_id in scar.get("animationBindings", []):
            behavior = _resolve_behavior(registry, behavior_id, biome_id)
            if behavior is not None:
                bindings.append(behavior["id"])
    return bindings
