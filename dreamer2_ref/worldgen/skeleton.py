"""Spatial skeleton pass.

Instantiates a layout idiom into a concrete 2D cell grid of void/floor/wall.
Geometry only; no meaning. Materials and meaning are assigned by later stages.
"""

from __future__ import annotations

import math
from typing import Any

from .cells import SemanticCell, SceneGraph
from .registry import Registry
from .scene_equation import SceneEquation
from .streams import stream


DEFAULT_WIDTH = 64
DEFAULT_HEIGHT = 22
MIN_WIDTH = 24
MIN_HEIGHT = 10


def instantiate(
    equation: SceneEquation,
    registry: Registry,
    *,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
) -> SceneGraph:
    # Enforce a minimum grid so topology passes never produce degenerate
    # scenes (negative radii, inner ring larger than outer ring, etc.).
    width = max(MIN_WIDTH, width)
    height = max(MIN_HEIGHT, height)

    cells = [
        [SemanticCell(type="void", material=None, openness=1.0) for _ in range(width)]
        for _ in range(height)
    ]
    scene = SceneGraph(
        equation=equation,
        width=width,
        height=height,
        cells=cells,
        pack_versions=registry.dump_versions(),
    )

    layout_id = equation.layout_idiom_id
    layout = registry.layouts.get(layout_id) if layout_id else None
    if layout is None:
        # Default to ring-sanctum when the equation omits a layout id.
        layout = registry.layouts.get("layout.ring-sanctum")
    if layout is None:
        _apply_single_hall(scene, equation, registry)
        return scene

    shape = layout["topology"].get("shape", "ring")
    if shape == "ring":
        _apply_ring_sanctum(scene, equation, registry, layout)
    elif shape == "single-hall":
        _apply_single_hall(scene, equation, registry)
    else:
        # Safe fallback: any unrecognized topology collapses to a single hall
        _apply_single_hall(scene, equation, registry)

    return scene


def _apply_ring_sanctum(
    scene: SceneGraph,
    equation: SceneEquation,
    registry: Registry,
    layout: dict[str, Any],
) -> None:
    width, height = scene.width, scene.height
    cx = width // 2
    cy = height // 2
    # Clamp radii so the ring remains well-formed even on small grids.
    outer_r = max(4, min(cx - 2, cy - 2))
    inner_r = max(3, min(outer_r - 3, outer_r - 6))
    if inner_r >= outer_r:
        inner_r = max(2, outer_r - 2)

    rng = stream(equation.seed, "skeleton.ring-sanctum")

    for y in range(height):
        for x in range(width):
            dx = x - cx
            dy = (y - cy) * 2  # terminal cells are taller than wide; double the y distance
            dist = math.sqrt(dx * dx + dy * dy)

            if dist <= inner_r - 1:
                # interior open floor, silence zone
                scene.cells[y][x].type = "floor"
                scene.cells[y][x].openness = 1.0
            elif dist <= inner_r + 0.5:
                # inner ring (sanctum rim)
                scene.cells[y][x].type = "arch"
                scene.cells[y][x].openness = 0.55
            elif dist <= outer_r - 0.5:
                # ambulatory floor
                scene.cells[y][x].type = "floor"
                scene.cells[y][x].openness = 0.85
            elif dist <= outer_r + 0.5:
                # outer wall
                scene.cells[y][x].type = "wall"
                scene.cells[y][x].openness = 0.1
            else:
                # void beyond sanctum
                scene.cells[y][x].type = "void"
                scene.cells[y][x].openness = 1.0

    # carve a single entry lane on the left to break perfect symmetry
    lane_y = cy + rng.randint(-1, 1)
    for x in range(1, cx - inner_r + 1):
        if 0 <= lane_y < height:
            cell = scene.cells[lane_y][x]
            if cell.type != "void":
                cell.type = "floor"
                cell.openness = 0.95

    # carve a niche opposite the lane
    niche_y = cy + rng.randint(-1, 1)
    niche_x = min(cx + outer_r - 1, width - 2)
    if 0 <= niche_y < height and 0 <= niche_x < width:
        scene.cells[niche_y][niche_x].type = "niche"
        scene.cells[niche_y][niche_x].openness = 0.6


def _apply_single_hall(scene: SceneGraph, equation: SceneEquation, registry: Registry) -> None:
    width, height = scene.width, scene.height
    for y in range(height):
        for x in range(width):
            cell = scene.cells[y][x]
            if y == 0 or y == height - 1 or x == 0 or x == width - 1:
                cell.type = "wall"
                cell.openness = 0.1
            else:
                cell.type = "floor"
                cell.openness = 0.9
