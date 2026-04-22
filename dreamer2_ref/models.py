from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SceneGeometry:
    width: int
    height: int
    content_height: int
    left_width: int
    seam_x: int
    portrait_origin_x: int
    portrait_origin_y: int
    ui_origin_x: int
    command_origin_y: int


@dataclass(slots=True)
class SceneTransition:
    source_mode_id: str
    target_mode_id: str
    style: str
    started_at: float
    duration_seconds: float

    def active(self, now: float) -> bool:
        return now <= self.started_at + self.duration_seconds

    def progress(self, now: float) -> float:
        if self.duration_seconds <= 0:
            return 1.0
        elapsed = max(0.0, now - self.started_at)
        return min(1.0, elapsed / self.duration_seconds)

    def to_spec(self, now: float) -> dict[str, object]:
        return {
            "sourceModeId": self.source_mode_id,
            "targetModeId": self.target_mode_id,
            "style": self.style,
            "progress": round(self.progress(now), 3),
        }


@dataclass(slots=True)
class SceneModel:
    profile_id: str
    mode_id: str
    capability_tier: str
    layers: list[str]
    randomness_streams: dict[str, str]
    active_events: list[str]
    motion_budget: dict[str, str]
    glitch_budget: str
    geometry: SceneGeometry
    notes: str
    transition: dict[str, object] | None = None

    def to_spec(self) -> dict[str, object]:
        spec = {
            "profileId": self.profile_id,
            "modeId": self.mode_id,
            "capabilityTier": self.capability_tier,
            "layers": list(self.layers),
            "randomnessStreams": dict(self.randomness_streams),
            "activeEvents": list(self.active_events),
            "notes": self.notes,
        }
        if self.transition is not None:
            spec["transition"] = dict(self.transition)
        return spec
