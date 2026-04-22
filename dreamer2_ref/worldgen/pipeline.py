"""Pipeline orchestrator.

Runs the nine conceptual stages from WORLD_GENERATION.md:

1. spatial skeleton
2. invisible world fields
3. biome grammar
4. story scars
5. focal object pass
6. atmospheric pass
7. companion integration
8. render synthesis (shell)
9. runtime animation binding

Stages 1-7 operate on the semantic scene graph. Stage 8 is synthesis.
Stage 9 is the animation binding pass (static bindings for Slice 3;
runtime advancement happens in the shell loop).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

from .animation import bind as bind_animation
from .atmosphere import apply as apply_atmosphere
from .biome import apply_grammar as apply_biome
from .cells import SceneGraph, RenderedCell
from .fields import seed_base as seed_fields
from .focal import install as install_focal
from .integration import place_companion
from .registry import Registry, load_registry
from .scars import apply as apply_scars
from .scene_equation import SceneEquation
from .skeleton import instantiate as instantiate_skeleton
from .synthesis import synthesize as synthesize_cells, render_to_text as _render_to_text


def generate_scene(
    equation: SceneEquation,
    registry: Registry,
    *,
    memory_tags: Optional[Iterable[str]] = None,
    width: int = 64,
    height: int = 22,
) -> SceneGraph:
    scene = instantiate_skeleton(equation, registry, width=width, height=height)
    seed_fields(scene, equation, registry)
    apply_biome(scene, equation, registry)
    install_focal(scene, equation, registry)
    apply_scars(scene, equation, registry, memory_tags or [])
    apply_atmosphere(scene, equation, registry)
    place_companion(scene, equation, registry)
    bind_animation(scene, equation, registry)
    return scene


def synthesize(
    scene: SceneGraph,
    registry: Registry,
    *,
    tier: str = "pure-text",
) -> List[List[RenderedCell]]:
    return synthesize_cells(scene, scene.equation, registry, tier=tier)


def render_to_text(
    rendered: List[List[RenderedCell]],
    *,
    colorize: bool = False,
) -> str:
    return _render_to_text(rendered, colorize=colorize)
