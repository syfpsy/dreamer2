from __future__ import annotations

import argparse
import json
import mimetypes
import threading
import webbrowser
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .app import DreamerApp


WEB_ASSET_ROOT = Path(__file__).resolve().parent / "web_assets"


@dataclass(slots=True)
class PreviewService:
    app: DreamerApp
    asset_root: Path
    lock: threading.Lock

    @property
    def valid_tiers(self) -> set[str]:
        return set(self.app.assets.capability_profiles.keys())

    def frame(self, tier: str | None = None) -> dict[str, object]:
        with self.lock:
            return self.app.snapshot_preview_payload(tier_override=self._resolve_tier(tier))

    def execute(self, command: str, tier: str | None = None) -> dict[str, object]:
        with self.lock:
            if command.strip():
                self.app._execute_command(command)
                self.app._save_state()
            return self.app.snapshot_preview_payload(tier_override=self._resolve_tier(tier))

    def read_asset(self, asset_path: str) -> tuple[bytes, str] | None:
        relative_path = asset_path.lstrip("/") or "index.html"
        candidate = (self.asset_root / relative_path).resolve()
        if self.asset_root.resolve() not in candidate.parents and candidate != self.asset_root.resolve():
            return None
        if not candidate.exists() or not candidate.is_file():
            return None

        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
        }.get(candidate.suffix.lower(), mimetypes.guess_type(str(candidate))[0] or "application/octet-stream")
        return (candidate.read_bytes(), content_type)

    def _resolve_tier(self, tier: str | None) -> str | None:
        if tier in self.valid_tiers:
            return tier
        return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dreamer2 web preview")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root containing config/, content/, packs/, and specs/",
    )
    parser.add_argument(
        "--tier",
        choices=["pure-text", "rich-unicode", "hybrid-graphics"],
        help="Initial capability tier for the preview.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Preview host interface.")
    parser.add_argument("--port", type=int, default=8765, help="Preview port.")
    parser.add_argument("--mode", help="Optional initial mode.")
    parser.add_argument(
        "--command",
        action="append",
        default=[],
        help="Execute one or more commands before the preview starts.",
    )
    parser.add_argument(
        "--with-relic",
        action="store_true",
        help="Force the starter relic visible before preview starts.",
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open the preview URL in the default browser after startup.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
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


def serve_preview(
    *,
    root: Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    tier_override: str | None = None,
    mode: str | None = None,
    initial_commands: list[str] | None = None,
    with_relic: bool = False,
    open_browser: bool = False,
) -> None:
    app = DreamerApp(root, tier_override=tier_override, no_color=True, use_diff=True)
    if mode and app._is_mode_available(mode):
        app.state["modeId"] = mode
    if with_relic:
        app._ensure_reference_relic()
    for command in initial_commands or []:
        app._execute_command(command)
    app._save_state()

    service = PreviewService(app=app, asset_root=WEB_ASSET_ROOT, lock=threading.Lock())
    handler = _build_handler(service)
    server = ThreadingHTTPServer((host, port), handler)
    preview_url = f"http://{host}:{port}/"

    print(f"Dreamer2 web preview listening at {preview_url}")
    if open_browser:
        webbrowser.open(preview_url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        app._save_state()


def _build_handler(service: PreviewService) -> type[BaseHTTPRequestHandler]:
    class PreviewHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/api/frame":
                query = parse_qs(parsed.query)
                tier = query.get("tier", [None])[0]
                self._send_json(service.frame(tier))
                return

            asset_path = "index.html" if parsed.path in {"", "/"} else parsed.path.lstrip("/")
            asset = service.read_asset(asset_path)
            if asset is None:
                self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
                return

            body, content_type = asset
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/api/command":
                self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
                return

            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            try:
                payload = json.loads(raw_body.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self.send_error(HTTPStatus.BAD_REQUEST, "Invalid JSON body")
                return

            command = str(payload.get("command", "")).strip()
            tier = payload.get("tier")
            response = service.execute(command, str(tier) if tier is not None else None)
            self._send_json(response)

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _send_json(self, payload: dict[str, object]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return PreviewHandler


if __name__ == "__main__":
    raise SystemExit(main())
