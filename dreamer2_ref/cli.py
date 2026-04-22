from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .app import DreamerApp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dreamer2 pure-text reference runtime")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root containing config/, content/, packs/, and specs/",
    )
    parser.add_argument(
        "--tier",
        choices=["pure-text", "rich-unicode", "hybrid-graphics"],
        help="Override automatic capability detection.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Render a single frame snapshot to stdout and exit.",
    )
    parser.add_argument(
        "--command",
        action="append",
        default=[],
        help="Execute one or more commands before rendering or exiting.",
    )
    parser.add_argument(
        "--mode",
        choices=["standby", "listening", "thinking", "building", "researching", "dreaming", "recovering", "focused"],
        help="Use a specific mode for --once rendering.",
    )
    parser.add_argument(
        "--with-relic",
        action="store_true",
        help="Force the starter relic visible for one-shot rendering.",
    )
    parser.add_argument(
        "--demo-seconds",
        type=float,
        default=0.0,
        help="Run a short animation demo and exit.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI styling.",
    )
    parser.add_argument(
        "--no-diff",
        action="store_true",
        help="Disable diff-based redraw in interactive mode.",
    )
    parser.add_argument(
        "--web-preview",
        action="store_true",
        help="Run the optional local browser preview instead of the terminal session.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface for --web-preview.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port for --web-preview.",
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open the local preview URL when --web-preview starts.",
    )
    parser.add_argument(
        "--dump-scene",
        action="store_true",
        help="Print the current scene model as JSON and exit.",
    )
    parser.add_argument(
        "--dump-render-state",
        action="store_true",
        help="Print the current render-state snapshot as JSON and exit.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.web_preview:
        from .web import serve_preview

        serve_preview(
            root=args.root.resolve(),
            host=args.host,
            port=args.port,
            tier_override=args.tier,
            mode=args.mode,
            initial_commands=args.command,
            with_relic=args.with_relic,
            open_browser=args.open_browser,
        )
        return 0

    app = DreamerApp(
        args.root.resolve(),
        tier_override=args.tier,
        no_color=args.no_color,
        use_diff=not args.no_diff,
    )

    if args.mode:
        app.state["modeId"] = args.mode
    if args.with_relic:
        app._ensure_reference_relic()
    for command in args.command:
        app._execute_command(command)

    if args.dump_scene:
        print(json.dumps(app.snapshot_scene_model(), indent=2))
        return 0

    if args.dump_render_state:
        print(json.dumps(app.snapshot_render_state(), indent=2))
        return 0

    if args.once:
        snapshot = app.run_once()
        if not _stdout_can_encode(snapshot) and app.tier != "pure-text":
            app.tier = "pure-text"
            snapshot = app.run_once()
        print(snapshot)
        return 0

    if args.demo_seconds > 0:
        app.run_demo(args.demo_seconds)
        return 0

    app.run_interactive()
    return 0


def _stdout_can_encode(text: str) -> bool:
    encoding = sys.stdout.encoding or "utf-8"
    try:
        text.encode(encoding)
    except UnicodeEncodeError:
        return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())
