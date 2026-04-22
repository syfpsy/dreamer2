"""Semantic cell model and scene graph structures.

A SemanticCell is the smallest addressable unit of meaning. The renderer
reads cells and assigns glyphs within the cell's declared glyph family.
Cells are renderer-independent and can be diffed, serialized, or
regenerated without touching glyph choice.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


GLYPH_FAMILIES = (
    "structural",
    "soft-signal",
    "dense-pressure",
    "decay",
    "symbolic",
)

PALETTE_ROLES = ("structural", "dim_support", "energy_or_event", "rare_anomaly")


@dataclass
class SemanticCell:
    type: str = "void"
    material: Optional[str] = None
    openness: float = 1.0
    light_exposure: float = 0.0
    fields: Dict[str, float] = field(default_factory=dict)
    glyph_family: str = "soft-signal"
    palette_role: str = "dim_support"
    active_state: str = "inert"
    prop_occupancy: Optional[str] = None
    motif_tag: Optional[str] = None
    motion_tag: Optional[str] = None
    dominant_influences: List[str] = field(default_factory=list)

    def field_value(self, field_id: str, default: float = 0.0) -> float:
        return self.fields.get(field_id, default)


@dataclass
class AnimationBinding:
    target: str
    behavior_id: str
    cell_xy: Optional[tuple] = None
    region: Optional[str] = None
    budget_cost: str = "low"


@dataclass
class SceneGraph:
    equation: "SceneEquation"
    width: int
    height: int
    cells: List[List[SemanticCell]]
    bindings: List[AnimationBinding] = field(default_factory=list)
    pack_versions: Dict[str, str] = field(default_factory=dict)
    applied_scars: List[str] = field(default_factory=list)
    companion_mode_id: Optional[str] = None
    focal_cell: Optional[tuple] = None

    def cell_at(self, x: int, y: int) -> SemanticCell:
        return self.cells[y][x]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height


@dataclass
class RenderedCell:
    glyph: str
    palette_role: str
    density: float
    glyph_family: str


# Back-reference for type hinting only; avoids a circular import.
from . import scene_equation as _scene_equation  # noqa: E402
SceneEquation = _scene_equation.SceneEquation  # type: ignore
