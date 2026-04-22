from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RuntimeAssets:
    root: Path
    app_config: dict[str, Any]
    profile: dict[str, Any]
    registry: dict[str, Any]
    theme: dict[str, Any]
    portrait_pack: dict[str, Any]
    portrait_parts: dict[str, dict[str, Any]]
    module_packs: dict[str, dict[str, Any]]
    commands: dict[str, dict[str, Any]]
    modes: dict[str, dict[str, Any]]
    panels: dict[str, dict[str, Any]]
    artifacts: dict[str, dict[str, Any]]
    ambient_behaviors: dict[str, dict[str, Any]]
    micromotion: dict[str, dict[str, Any]]
    distortion_presets: dict[str, dict[str, Any]]
    capability_profiles: dict[str, dict[str, Any]]
    companions: dict[str, dict[str, Any]]
    evolution_rules: dict[str, dict[str, Any]]


CONTENT_KEYS = {
    "commands": "commands",
    "modes": "modes",
    "panels": "panels",
    "artifacts": "artifactTypes",
    "ambientBehaviors": "ambientBehaviors",
    "microMotion": "microMotion",
    "distortionPresets": "distortionPresets",
    "capabilities": "capabilityProfiles",
    "companions": "entities",
    "evolution": "rules",
}


def load_assets(root: Path) -> RuntimeAssets:
    app_config = _load_json(root / "config" / "defaults" / "app.config.example.json")
    profile = _load_json(root / "config" / "defaults" / "companion.profile.example.json")
    registry = _load_json(root / "config" / "defaults" / "runtime.registry.example.json")

    themes = _discover_by_id(root / "packs" / "themes", "theme.json")
    portrait_packs = _discover_by_id(root / "packs" / "portrait", "pack.json")
    module_packs = _discover_by_id(root / "packs" / "modules", "pack.json")

    theme = themes[app_config["defaultThemeId"]]
    portrait_pack = portrait_packs[app_config["loadedPortraitPacks"][0]]
    loaded_module_packs = {
        pack_id: module_packs[pack_id]
        for pack_id in app_config["loadedModulePacks"]
        if pack_id in module_packs
    }

    portrait_parts: dict[str, dict[str, Any]] = {}
    portrait_pack_path = Path(portrait_pack["__path__"])
    for part_ref in portrait_pack["partRefs"]:
        part = _load_json((portrait_pack_path.parent / part_ref).resolve())
        part["__path__"] = str((portrait_pack_path.parent / part_ref).resolve())
        portrait_parts[part["id"]] = part

    content_indexes: dict[str, dict[str, dict[str, Any]]] = {}
    for registry_key, collection_key in CONTENT_KEYS.items():
        content_indexes[registry_key] = _load_content_registry(
            root, registry["content"].get(registry_key, []), collection_key
        )

    return RuntimeAssets(
        root=root,
        app_config=app_config,
        profile=profile,
        registry=registry,
        theme=theme,
        portrait_pack=portrait_pack,
        portrait_parts=portrait_parts,
        module_packs=loaded_module_packs,
        commands=content_indexes["commands"],
        modes=content_indexes["modes"],
        panels=content_indexes["panels"],
        artifacts=content_indexes["artifacts"],
        ambient_behaviors=content_indexes["ambientBehaviors"],
        micromotion=content_indexes["microMotion"],
        distortion_presets=content_indexes["distortionPresets"],
        capability_profiles=content_indexes["capabilities"],
        companions=content_indexes["companions"],
        evolution_rules=content_indexes["evolution"],
    )


def _discover_by_id(root: Path, filename: str) -> dict[str, dict[str, Any]]:
    manifests: dict[str, dict[str, Any]] = {}
    for path in root.rglob(filename):
        manifest = _load_json(path)
        manifest["__path__"] = str(path.resolve())
        manifests[manifest["id"]] = manifest
    return manifests


def _load_content_registry(
    root: Path, relative_paths: list[str], collection_key: str
) -> dict[str, dict[str, Any]]:
    items: dict[str, dict[str, Any]] = {}
    for relative_path in relative_paths:
        payload = _load_json(root / relative_path)
        for item in payload.get(collection_key, []):
            items[item["id"]] = item
    return items


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
