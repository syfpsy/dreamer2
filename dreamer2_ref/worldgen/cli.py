"""CLI for the world-generation pipeline.

Usage:
    python -m dreamer2_ref.worldgen
    python -m dreamer2_ref.worldgen --equation packs/world/scene-equations/signal-chapel-reverent-instability.json
    python -m dreamer2_ref.worldgen --memory-tag failed-extraction
    python -m dreamer2_ref.worldgen --seed alt-seed --memory-tag failed-extraction --colorize

Prints the rendered scene as text. Passes --colorize to emit ANSI color.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional

from .pipeline import generate_scene, synthesize, render_to_text
from .registry import load_registry
from .scene_equation import SceneEquation


DEFAULT_EQUATION_PATH = "packs/world/scene-equations/signal-chapel-reverent-instability.json"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Dreamer2 world-generation pipeline")
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parent.parent.parent),
        help="Repository root (defaults to the dreamer2 root).",
    )
    parser.add_argument(
        "--equation",
        default=None,
        help="Scene equation JSON path (defaults to the Signal Chapel preset).",
    )
    parser.add_argument(
        "--seed",
        default=None,
        help="Override the scene equation seed.",
    )
    parser.add_argument(
        "--memory-tag",
        dest="memory_tags",
        action="append",
        default=[],
        help="Memory tag hint (can be repeated); may trigger conditional scars.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=64,
    )
    parser.add_argument(
        "--height",
        type=int,
        default=22,
    )
    parser.add_argument(
        "--colorize",
        action="store_true",
        help="Emit ANSI color escapes per palette role.",
    )

    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    registry = load_registry(root)

    equation_path = Path(args.equation) if args.equation else (root / DEFAULT_EQUATION_PATH)
    equation = SceneEquation.from_file(equation_path)
    if args.seed:
        equation.seed = args.seed

    scene = generate_scene(
        equation,
        registry,
        memory_tags=args.memory_tags,
        width=args.width,
        height=args.height,
    )
    rendered = synthesize(scene, registry)
    text = render_to_text(rendered, colorize=args.colorize)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
