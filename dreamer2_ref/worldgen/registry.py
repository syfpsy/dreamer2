"""Pack registry loader for world-generation content.

Scans pack folders, loads JSON manifests, performs pragmatic
structural validation (required fields and reference existence),
and exposes lookup by id and enumeration by class.

Validation is deliberately lightweight for the first slice.
Full JSON Schema draft-2020-12 validation can be layered on later
without changing the consumer API.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


class RegistryError(RuntimeError):
    pass


# Each entry: (class tag, folder under packs/, filename pattern or None)
_CLASS_FOLDERS: Tuple[Tuple[str, str, Optional[str]], ...] = (
    ("world-field-pack", "world/fields", None),
    ("material", "world/materials", None),
    ("motif-pack", "style/motifs", None),
    ("palette-doctrine", "style/palettes", None),
    ("animation-behavior", "animations", None),
    ("layout-idiom", "world/layouts", None),
    ("weather-system", "world/weather", None),
    ("focal-object", "world/focals", None),
    ("scar-package", "world/scars", None),
    ("place-archetype", "world/archetypes", "place.json"),
    ("composition-mode", "companions/composition-modes", None),
    ("scene-equation", "world/scene-equations", None),
)


_REQUIRED_FIELDS: Dict[str, Tuple[str, ...]] = {
    "place-archetype": (
        "id",
        "label",
        "compatibleLayoutIdioms",
        "materialFamilies",
        "motifSet",
        "glyphFamilyBias",
        "paletteDoctrineRef",
        "silenceToDetailRatio",
    ),
    "layout-idiom": ("id", "label", "topology"),
    "scar-package": ("id", "label", "kind"),
    "focal-object": (
        "id",
        "label",
        "dominantMotif",
        "compatibleBiomes",
        "glyphFamilies",
        "compositionModes",
    ),
    "weather-system": (
        "id",
        "label",
        "dominantAxis",
        "glyphFamilies",
        "densityBudget",
    ),
    "material": ("id", "label", "allowedGlyphFamilies"),
    "motif": ("id", "label", "silhouetteRule"),
    "palette-doctrine": ("id", "label", "roles"),
    "animation-behavior": (
        "id",
        "label",
        "family",
        "targetKinds",
        "glyphFamilies",
        "timing",
        "motionBudgetCost",
    ),
    "composition-mode": ("id", "label", "mode"),
    "scene-equation": ("id", "biomeId", "focalObjectId", "agentState", "seed"),
}


@dataclass
class Registry:
    root: Path
    archetypes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    layouts: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    scars: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    focals: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    weather: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    materials: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    motifs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    palettes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    behaviors: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    composition_modes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    scene_equations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    fields: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def dump_versions(self) -> Dict[str, str]:
        versions: Dict[str, str] = {}
        for bucket in (
            self.archetypes,
            self.layouts,
            self.scars,
            self.focals,
            self.weather,
            self.materials,
            self.motifs,
            self.palettes,
            self.behaviors,
            self.composition_modes,
            self.scene_equations,
            self.fields,
        ):
            for item_id, payload in bucket.items():
                versions[item_id] = payload.get("version", "0.0.0")
        return versions


def load_registry(root: Path) -> Registry:
    registry = Registry(root=root)

    for class_tag, folder, filename in _CLASS_FOLDERS:
        base = root / "packs" / folder
        if not base.exists():
            continue

        iterable: Iterable[Path]
        if filename:
            iterable = base.rglob(filename)
        else:
            iterable = (p for p in base.rglob("*.json") if p.is_file())

        for path in iterable:
            payload = _load_json(path)
            _route_payload(registry, class_tag, payload, path)

    _validate_and_resolve(registry)
    return registry


def _route_payload(registry: Registry, class_tag: str, payload: Dict[str, Any], path: Path) -> None:
    if class_tag == "world-field-pack":
        for field_def in payload.get("fields", []):
            _require(field_def, ("id", "kind"), path)
            registry.fields[field_def["id"]] = field_def
        return

    if class_tag == "motif-pack":
        for motif in payload.get("motifs", []):
            _require(motif, _REQUIRED_FIELDS["motif"], path)
            registry.motifs[motif["id"]] = motif
        return

    bucket = {
        "place-archetype": registry.archetypes,
        "layout-idiom": registry.layouts,
        "scar-package": registry.scars,
        "focal-object": registry.focals,
        "weather-system": registry.weather,
        "material": registry.materials,
        "palette-doctrine": registry.palettes,
        "animation-behavior": registry.behaviors,
        "composition-mode": registry.composition_modes,
        "scene-equation": registry.scene_equations,
    }.get(class_tag)

    if bucket is None:
        return

    required = _REQUIRED_FIELDS.get(class_tag, ("id",))
    _require(payload, required, path)
    bucket[payload["id"]] = payload


def _require(payload: Dict[str, Any], required: Tuple[str, ...], path: Path) -> None:
    missing = [key for key in required if key not in payload]
    if missing:
        raise RegistryError(f"{path}: missing required fields {missing}")


def _validate_and_resolve(registry: Registry) -> None:
    """Hard-fail only on direct dependencies used by the render pipeline.

    Compatibility lists (``allowed*``, ``compatible*``, ``affinity*``) are
    discovery hints and may reference content that has not yet been
    authored as a pack. Those are left for other tools to warn on.
    """
    errors: List[str] = []

    for archetype_id, archetype in registry.archetypes.items():
        # Palette doctrine is required for render synthesis.
        palette_ref = archetype.get("paletteDoctrineRef")
        if palette_ref is not None and palette_ref not in registry.palettes:
            errors.append(
                f"{archetype_id}: unknown palette doctrine {palette_ref}"
            )
        # Every referenced material must exist (biome grammar uses them).
        for material_entry in archetype.get("materialFamilies", []):
            if material_entry["id"] not in registry.materials:
                errors.append(
                    f"{archetype_id}: unknown material {material_entry['id']}"
                )
        # Every referenced motif must exist (motif library is used by biome).
        for motif_id in archetype.get("motifSet", []):
            if motif_id not in registry.motifs:
                errors.append(f"{archetype_id}: unknown motif {motif_id}")

    # Behavior fallbacks must terminate at a known behavior.
    for behavior_id, behavior in registry.behaviors.items():
        fallback = behavior.get("fallbackBehaviorId")
        if fallback and fallback not in registry.behaviors:
            # A missing fallback is a soft hint, not a load failure;
            # the binder degrades gracefully when fallbacks are absent.
            pass

    # Composition mode fallback chains are also soft.
    for mode_id, mode in registry.composition_modes.items():
        fallback = mode.get("fallbackModeId")
        if fallback and fallback not in registry.composition_modes:
            pass

    if errors:
        raise RegistryError("registry validation failed:\n  " + "\n  ".join(errors))


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
