"""Scene equation object and loader.

The scene equation is a first-class object. Every scene keeps a
reference to its equation so the system can regenerate, remix,
share, and inspect scenes by story rather than by coordinate.

scene = Biome + StoryEvent + Mood + FocalObject + EnvironmentalWeather
      + ScarType + AgentState + MemoryEcho
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class SceneEquation:
    biome_id: str
    focal_object_id: str
    agent_state: str
    seed: Union[str, int]
    id: Optional[str] = None
    label: Optional[str] = None
    layout_idiom_id: Optional[str] = None
    weather_id: Optional[str] = None
    scar_ids: List[str] = field(default_factory=list)
    composition_mode_id: Optional[str] = None
    memory_echo_refs: List[str] = field(default_factory=list)
    mood: Optional[str] = None
    pack_versions: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "biomeId": self.biome_id,
            "layoutIdiomId": self.layout_idiom_id,
            "focalObjectId": self.focal_object_id,
            "weatherId": self.weather_id,
            "scarIds": list(self.scar_ids),
            "agentState": self.agent_state,
            "compositionModeId": self.composition_mode_id,
            "memoryEchoRefs": list(self.memory_echo_refs),
            "seed": self.seed,
            "mood": self.mood,
            "packVersions": dict(self.pack_versions),
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "SceneEquation":
        return cls(
            id=payload.get("id"),
            label=payload.get("label"),
            biome_id=payload["biomeId"],
            layout_idiom_id=payload.get("layoutIdiomId"),
            focal_object_id=payload["focalObjectId"],
            weather_id=payload.get("weatherId"),
            scar_ids=list(payload.get("scarIds", [])),
            agent_state=payload.get("agentState", "listening"),
            composition_mode_id=payload.get("compositionModeId"),
            memory_echo_refs=list(payload.get("memoryEchoRefs", [])),
            seed=payload.get("seed", 0),
            mood=payload.get("mood"),
            pack_versions=dict(payload.get("packVersions", {})),
        )

    @classmethod
    def from_file(cls, path: Path) -> "SceneEquation":
        with path.open("r", encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))
