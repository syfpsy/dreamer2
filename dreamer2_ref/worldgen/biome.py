"""Biome grammar application.

Once the spatial skeleton is in place, the biome grammar chooses
materials for each semantic cell, assigns the cell's glyph family
and palette role, and records dominant motif tags where appropriate.
All choices remain semantic; no glyph characters are picked here.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .cells import GLYPH_FAMILIES, SceneGraph
from .registry import Registry
from .scene_equation import SceneEquation
from .streams import stream


def apply_grammar(scene: SceneGraph, equation: SceneEquation, registry: Registry) -> None:
    archetype = registry.archetypes.get(equation.biome_id)
    if archetype is None:
        return

    material_families: List[Dict[str, Any]] = archetype.get("materialFamilies", [])
    if not material_families:
        return

    rng = stream(equation.seed, "biome.material-assignment")
    family_weights = archetype.get("glyphFamilyBias", {})

    for y, row in enumerate(scene.cells):
        for x, cell in enumerate(row):
            if cell.type == "void":
                cell.glyph_family = "soft-signal"
                cell.palette_role = "dim_support"
                continue

            material_id = _pick_material(material_families, cell.type, rng)
            cell.material = material_id
            material = registry.materials.get(material_id, {})
            cell.glyph_family = _pick_glyph_family(
                cell.type, material, family_weights, stream(equation.seed, f"cell.{x}.{y}.family")
            )
            cell.palette_role = _pick_palette_role(cell.type, material)

            # Dominant motif tagging for arches, niches, and the inner ring.
            if cell.type == "arch":
                cell.motif_tag = "motif.stepped-halo"
            elif cell.type == "niche":
                cell.motif_tag = "motif.prayer-bracket"

    # Record silence ratio by marking peripheral cells quieter.
    silence_ratio = float(archetype.get("silenceToDetailRatio", 0.7))
    _apply_silence_ratio(scene, silence_ratio, stream(equation.seed, "biome.silence"))


def _pick_material(material_families: List[Dict[str, Any]], cell_type: str, rng) -> str:
    if cell_type in ("wall", "arch"):
        # Favor structural materials for walls and arches.
        for entry in material_families:
            if entry["id"].startswith("material.shrine-plating"):
                return entry["id"]
        return material_families[0]["id"]

    if cell_type == "niche":
        for entry in material_families:
            if entry["id"].startswith("material.cable-veined-stone"):
                return entry["id"]
        return material_families[0]["id"]

    # Floors: weighted random from the declared families.
    total = sum(entry["baseRatio"] for entry in material_families)
    pick = rng.random() * total
    accum = 0.0
    for entry in material_families:
        accum += entry["baseRatio"]
        if pick <= accum:
            return entry["id"]
    return material_families[-1]["id"]


def _pick_glyph_family(
    cell_type: str,
    material: Dict[str, Any],
    archetype_bias: Dict[str, float],
    rng,
) -> str:
    if cell_type in ("wall", "arch"):
        return "structural"

    allowed = material.get("allowedGlyphFamilies") or []
    if not allowed:
        return "soft-signal"

    weights: Dict[str, float] = {}
    for entry in allowed:
        family = entry["family"]
        material_weight = float(entry.get("weight", 0.0))
        biome_weight = float(archetype_bias.get(family, 1.0))
        weights[family] = material_weight * biome_weight

    if cell_type == "floor":
        weights["structural"] = weights.get("structural", 0.0) * 0.4
        weights["soft-signal"] = weights.get("soft-signal", 0.0) + 0.1

    total = sum(weights.values())
    if total <= 0:
        return "soft-signal"
    pick = rng.random() * total
    accum = 0.0
    for family, weight in weights.items():
        accum += weight
        if pick <= accum:
            return family
    return "soft-signal"


def _pick_palette_role(cell_type: str, material: Dict[str, Any]) -> str:
    preferred = material.get("preferredPaletteRoles") or []
    if cell_type in ("wall", "arch"):
        return "structural"
    if cell_type == "niche":
        return "dim_support"
    if preferred:
        return preferred[0]
    return "dim_support"


def _apply_silence_ratio(scene: SceneGraph, silence_ratio: float, rng) -> None:
    for y, row in enumerate(scene.cells):
        for x, cell in enumerate(row):
            if cell.type in ("wall", "arch", "niche"):
                continue
            if cell.type == "floor" and cell.glyph_family not in ("structural",):
                if rng.random() < silence_ratio:
                    cell.active_state = "inert"
                else:
                    cell.active_state = "humming"
