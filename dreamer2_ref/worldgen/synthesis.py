"""Render synthesis: semantic scene graph -> rendered cells.

This is the LAST pass. Glyph choices are made here, within the cell's
declared glyph family. Palette roles are mapped to ANSI 8-color
fallbacks for pure-text. The synthesizer never chooses meaning; it
chooses expression.
"""

from __future__ import annotations

from typing import Dict, List

from .cells import RenderedCell, SceneGraph
from .registry import Registry
from .scene_equation import SceneEquation
from .streams import stable_hash


GLYPH_POOLS: Dict[str, List[str]] = {
    "structural": ["|", "/", "\\", "_", "-", "[", "]", "(", ")", "<", ">"],
    "soft-signal": [".", ",", "'", ":", "~"],
    "dense-pressure": ["#", "%", "@", "=", "+"],
    "decay": [";", "^", "x", "!", "?"],
    "symbolic": ["*", "+", "o", "O"],
}


# Per glyph family, tier-aware constrained pools can be added later.
STRUCTURAL_BY_TYPE: Dict[str, List[str]] = {
    "wall": ["|", "_", "-"],
    "arch": ["(", ")", "[", "]", "<", ">"],
    "niche": ["[", "]", "|"],
    "altar": ["=", "-", "_"],
    "floor": [" "],
    "void": [" "],
}


ANSI_ROLE_FG: Dict[str, str] = {
    "structural": "37",
    "dim_support": "90",
    "energy_or_event": "36",
    "rare_anomaly": "33",
}


def synthesize(
    scene: SceneGraph,
    equation: SceneEquation,
    registry: Registry,
    *,
    tier: str = "pure-text",
) -> List[List[RenderedCell]]:
    rows: List[List[RenderedCell]] = []
    for y in range(scene.height):
        row: List[RenderedCell] = []
        for x in range(scene.width):
            cell = scene.cell_at(x, y)
            row.append(_synthesize_cell(cell, equation, x, y))
        rows.append(row)
    return rows


def _synthesize_cell(cell, equation: SceneEquation, x: int, y: int) -> RenderedCell:
    if cell.type == "void":
        return RenderedCell(
            glyph=" ",
            palette_role="dim_support",
            density=0.0,
            glyph_family="soft-signal",
        )

    glyph = _pick_glyph(cell, equation, x, y)
    return RenderedCell(
        glyph=glyph,
        palette_role=cell.palette_role,
        density=_density_for(cell),
        glyph_family=cell.glyph_family,
    )


def _pick_glyph(cell, equation: SceneEquation, x: int, y: int) -> str:
    if cell.type in ("wall", "arch", "niche", "altar"):
        pool = STRUCTURAL_BY_TYPE.get(cell.type, GLYPH_POOLS["structural"])
        h = stable_hash(equation.seed, "glyph", cell.type, cell.material or "", x, y)
        return pool[h % len(pool)]

    family = cell.glyph_family
    # Structural floors remain quiet unless the cell is active or scarred.
    if cell.type == "floor" and cell.active_state == "inert" and family != "symbolic":
        return " "

    pool = GLYPH_POOLS.get(family, GLYPH_POOLS["soft-signal"])

    # Scarred cells tilt toward decay within their family constraints
    # unless the family explicitly forbids it (i.e., symbolic cells keep their role).
    if cell.active_state == "scarred" and family == "structural":
        pool = GLYPH_POOLS["decay"]

    # Altars/symbolic cells go to the symbolic pool.
    if family == "symbolic" and cell.type != "altar":
        pool = GLYPH_POOLS["symbolic"]

    h = stable_hash(equation.seed, "glyph", family, x, y, cell.active_state)
    return pool[h % len(pool)]


def _density_for(cell) -> float:
    base = 0.0
    if cell.type in ("wall", "arch", "niche", "altar"):
        base = 0.9
    elif cell.active_state == "humming":
        base = 0.35
    elif cell.active_state == "pulsing":
        base = 0.6
    elif cell.active_state == "ritual-active":
        base = 0.8
    elif cell.active_state == "scarred":
        base = 0.5
    return base


def render_to_text(
    rendered: List[List[RenderedCell]],
    *,
    colorize: bool = False,
) -> str:
    lines: List[str] = []
    for row in rendered:
        if not colorize:
            lines.append("".join(cell.glyph for cell in row))
            continue
        parts: List[str] = []
        last_color = None
        for cell in row:
            color = ANSI_ROLE_FG.get(cell.palette_role, "37")
            if color != last_color:
                parts.append(f"\x1b[{color}m")
                last_color = color
            parts.append(cell.glyph)
        parts.append("\x1b[0m")
        lines.append("".join(parts))
    return "\n".join(lines)
