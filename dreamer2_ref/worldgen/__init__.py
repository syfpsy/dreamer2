"""Dreamer2 world generation package.

Invisible-first pipeline: world logic becomes a semantic scene graph,
then a render synthesis pass turns that graph into glyphs and palette
assignments. The renderer is the last pass, not the first.

See WORLD_GENERATION.md, PLACE_GRAMMAR.md, ATMOSPHERE.md,
COMPANION_ORGANISM.md, ANIMATION_REGISTRY.md, GLYPH_LANGUAGE.md,
PACK_SYSTEM.md for the full doctrine.
"""

from .cells import SemanticCell, SceneGraph, RenderedCell
from .scene_equation import SceneEquation
from .registry import Registry, load_registry, RegistryError
from .pipeline import generate_scene, synthesize, render_to_text

__all__ = [
    "Registry",
    "RegistryError",
    "RenderedCell",
    "SceneEquation",
    "SceneGraph",
    "SemanticCell",
    "generate_scene",
    "load_registry",
    "render_to_text",
    "synthesize",
]
