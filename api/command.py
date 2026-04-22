from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent

os.environ.setdefault("DREAMER2_STATE_DIR", "/tmp/dreamer2-state")
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dreamer2_ref.app import DreamerApp  # noqa: E402


def _build_app(tier: str | None) -> DreamerApp:
    return DreamerApp(_ROOT, tier_override=tier, no_color=True, use_diff=True)


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", "0") or 0)
        raw_body = self.rfile.read(content_length) if content_length else b""

        try:
            payload_in = json.loads(raw_body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            body = json.dumps({"error": "Invalid JSON body"}).encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        command = str(payload_in.get("command", "")).strip()
        tier_raw = payload_in.get("tier")
        tier = str(tier_raw) if tier_raw is not None else None

        try:
            app = _build_app(tier)
            if command:
                app._execute_command(command)
                app._save_state()
            payload_out = app.snapshot_preview_payload(tier_override=tier)
        except Exception as exc:  # noqa: BLE001
            body = json.dumps({"error": str(exc)}).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        body = json.dumps(payload_out).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        return
