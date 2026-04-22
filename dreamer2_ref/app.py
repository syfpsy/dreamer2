from __future__ import annotations

import hashlib
import json
import math
import os
import select
import shutil
import sys
import time
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from textwrap import wrap
from typing import Any

from .assets import RuntimeAssets, load_assets
from .commands import parse_shell_input
from .memory import (
    append_session_event,
    create_dream_draft,
    forget_memory,
    inspect_memory_lines,
    load_runtime_state,
    promote_dream_draft,
    remember_from_text,
    revise_memory,
    save_runtime_state,
)
from .models import SceneGeometry, SceneModel, SceneTransition
from .render import AnsiDiffRenderer, CellGrid


GLYPH_FAMILIES = {
    "structural": list(r"|/\_-[]()<>"),
    "soft-signal": list(".,':~"),
    "dense-pressure": list("#%@=+"),
    "decay": list(";^x!?"),
    "symbolic": list("*+oO"),
}

TIER_GLYPH_OVERRIDES = {
    "rich-unicode": {
        "structural": list("│╎┆/\\_-[]()<>"),
        "soft-signal": list(".,':~·˙•"),
        "dense-pressure": list("#%@=+░▒▓"),
        "decay": list(";:x!?¸"),
        "symbolic": list("*+oO◦○✦"),
    },
    "hybrid-graphics": {
        "structural": list("│╎┆/\\_-[]()<>"),
        "soft-signal": list(".,':~·˙•"),
        "dense-pressure": list("#%@=+░▒▓"),
        "decay": list(";:x!?¸"),
        "symbolic": list("*+oO◦○✦"),
    },
}

FRAME_CHARSETS = {
    "pure-text": {
        "horizontal": "-",
        "vertical": "|",
        "top_left": "+",
        "top_right": "+",
        "bottom_left": "+",
        "bottom_right": "+",
    },
    "rich-unicode": {
        "horizontal": "─",
        "vertical": "│",
        "top_left": "┌",
        "top_right": "┐",
        "bottom_left": "└",
        "bottom_right": "┘",
    },
    "hybrid-graphics": {
        "horizontal": "─",
        "vertical": "│",
        "top_left": "┌",
        "top_right": "┐",
        "bottom_left": "└",
        "bottom_right": "┘",
    },
}

PART_STYLE = {
    "structural": "structural",
    "signal": "signal",
    "symbolic": "symbolic",
    "decay": "decay",
}


@dataclass(slots=True)
class TimedEvent:
    kind: str
    preset_id: str
    expires_at: float


class DreamerApp:
    def __init__(
        self,
        root: Path,
        *,
        tier_override: str | None = None,
        no_color: bool = False,
        use_diff: bool = True,
    ) -> None:
        self.root = root
        self.assets = load_assets(root)
        self.state = load_runtime_state(root, self.assets.profile)
        self.no_color = no_color
        self.use_diff = use_diff
        self.tier = detect_capability_tier(self.assets, tier_override=tier_override)
        self.input_buffer = ""
        self.should_exit = False
        self.frame_count = 0
        self.transient_events: list[TimedEvent] = []
        self.active_transition: SceneTransition | None = None
        self.renderer = AnsiDiffRenderer(use_diff=use_diff, no_color=no_color)
        self.frame_cadence = self.assets.app_config["shell"]["frameCadenceMs"] / 1000.0
        self.loaded_command_ids = self._collect_loaded_ids("commandIds")
        self.loaded_panel_ids = self._collect_loaded_ids("panelIds")
        self.loaded_companion_ids = self._collect_loaded_ids("companionIds")
        self.loaded_mode_ids = self._collect_loaded_ids("optionalModeIds") or sorted(self.assets.modes.keys())
        self.loaded_commands = {
            command_id: self.assets.commands[command_id]
            for command_id in self.loaded_command_ids
            if command_id in self.assets.commands
        }
        self.loaded_panels = {
            panel_id: self.assets.panels[panel_id]
            for panel_id in self.loaded_panel_ids
            if panel_id in self.assets.panels
        }
        self.command_verbs = {command["verb"] for command in self.loaded_commands.values()}
        self._sync_boot_log()
        if self.state["modeId"] not in self.loaded_mode_ids:
            self.state["modeId"] = self.assets.app_config["mind"]["defaultModeId"]

    def run_once(self, *, mode: str | None = None, with_relic: bool = False) -> str:
        original_mode = self.state["modeId"]
        if mode and self._is_mode_available(mode):
            self.state["modeId"] = mode
        if with_relic:
            self._ensure_reference_relic()
        grid = self._build_grid(time.monotonic())
        snapshot = self.renderer.snapshot(grid)
        self.state["modeId"] = original_mode
        return snapshot

    def snapshot_scene_model(self, now: float | None = None) -> dict[str, object]:
        timestamp = now if now is not None else time.monotonic()
        scene = self._build_scene_model(timestamp)
        return scene.to_spec()

    def snapshot_render_state(self, now: float | None = None) -> dict[str, object]:
        timestamp = now if now is not None else time.monotonic()
        scene = self._build_scene_model(timestamp)
        active_parts = self._active_parts()
        mode = self.assets.modes[self.state["modeId"]]
        distortion = self._active_distortion_profile()
        visible_panels = self._visible_panels()

        return {
            "profileId": self.assets.profile["profileId"],
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "modeId": self.state["modeId"],
            "capabilityTier": self.tier,
            "seed": {
                "identity": self.assets.profile["seed"]["identity"],
                "portrait": self.assets.profile["seed"]["portrait"],
                "ambient": self.assets.profile["seed"]["ambient"],
            },
            "scene": {
                "grid": {
                    "width": scene.geometry.width,
                    "height": scene.geometry.height,
                    "cellAspect": "terminal-default",
                },
                "layers": list(scene.layers),
                "motionBudget": dict(scene.motion_budget),
                "glitchBudget": scene.glitch_budget,
                **({"transition": scene.transition} if scene.transition is not None else {}),
            },
            "portrait": {
                "activeParts": active_parts,
                "layers": ["silhouette", "identity", "micro-motion", "ambient", "mode-overlay", "event"],
                "mutations": [artifact["type"] for artifact in self.state["artifacts"]],
                "artifactBindings": [artifact["id"] for artifact in self.state["artifacts"]],
                "companionBindings": [companion["id"] for companion in self._visible_companions()],
                "stabilityProfile": "iconic-stable",
                "mutationBudget": "low",
            },
            "ambientField": {
                "profile": mode["ambientProfile"],
                "density": self.assets.ambient_behaviors[mode["ambientProfile"]]["density"],
                "cadenceMs": self.assets.app_config["shell"]["frameCadenceMs"],
                "activeEntities": [companion["id"] for companion in self._visible_companions()],
                "behaviorIds": [mode["ambientProfile"]],
            },
            "panels": [panel["id"] for panel in visible_panels],
            "transmission": {
                "distortionProfile": distortion,
                "pendingLineStyle": "soft-cursor",
                "activePresetId": distortion,
                "readabilityFloor": self.assets.distortion_presets.get(distortion, {}).get("readabilityFloor", 1),
            },
            "redraw": {
                "strategy": "diff-regions" if self.use_diff else "full-frame",
                "maxChangedRegions": 18,
            },
        }

    def snapshot_preview_payload(
        self,
        *,
        now: float | None = None,
        tier_override: str | None = None,
    ) -> dict[str, object]:
        timestamp = now if now is not None else time.monotonic()
        original_tier = self.tier

        if tier_override is not None:
            self.tier = tier_override

        try:
            self._prune_events(timestamp)
            scene = self._build_scene_model(timestamp)
            grid = self._build_grid(timestamp)
            render_state = self.snapshot_render_state(timestamp)
            visible_artifacts = self._visible_artifacts()
            visible_companions = self._visible_companions()
            surface_focus = self._surface_focus()

            return {
                "timestamp": datetime.now(tz=UTC).isoformat(),
                "profile": {
                    "id": self.assets.profile["profileId"],
                    "displayName": self.assets.profile["displayName"],
                    "archetype": self.assets.profile["archetype"],
                    "seed": dict(self.assets.profile["seed"]),
                },
                "theme": {
                    "id": self.assets.theme["id"],
                    "colors": dict(self.assets.theme["colors"]),
                    "semanticRoles": dict(self.assets.theme["semanticRoles"]),
                },
                "scene": scene.to_spec(),
                "renderState": render_state,
                "shell": {
                    "modeId": self.state["modeId"],
                    "capabilityTier": self.tier,
                    "surfaceFocus": surface_focus,
                    "activeTransition": scene.transition,
                    "transmissionLog": list(self.state["transmissionLog"]),
                    "selectedMemory": self._selected_memory(),
                    "selectedArtifact": self._selected_artifact(visible_artifacts),
                    "visibleArtifacts": visible_artifacts,
                    "visibleCompanions": visible_companions,
                    "availableCommands": [command["verb"] for command in self._available_commands()],
                    "commandHints": self._command_hints(),
                    "surface": {
                        "title": self._panel_title({"id": "panel.memory.surface"}),
                        "lines": self._surface_lines(64),
                    },
                },
                "grid": grid.payload(),
            }
        finally:
            self.tier = original_tier

    def run_demo(self, seconds: float) -> None:
        with TerminalSession(self.renderer, self._save_state):
            deadline = time.monotonic() + seconds
            force_full = True
            while time.monotonic() < deadline:
                now = time.monotonic()
                self._prune_events(now)
                self.renderer.render(self._build_grid(now), force_full=force_full)
                force_full = False
                time.sleep(self.frame_cadence)

    def run_interactive(self) -> None:
        with TerminalSession(self.renderer, self._save_state), InputPump() as input_pump:
            force_full = True
            last_frame = 0.0
            while not self.should_exit:
                now = time.monotonic()
                if now - last_frame >= self.frame_cadence:
                    self._prune_events(now)
                    self.renderer.render(self._build_grid(now), force_full=force_full)
                    force_full = False
                    last_frame = now

                for char in input_pump.read():
                    self._handle_input_char(char)

                time.sleep(0.02)

    def _handle_input_char(self, char: str) -> None:
        if char in ("\r", "\n"):
            submitted = self.input_buffer.strip()
            self.input_buffer = ""
            if submitted:
                self._execute_command(submitted)
            return

        if char in ("\x08", "\x7f"):
            self.input_buffer = self.input_buffer[:-1]
            return

        if char == "\x03":
            self.should_exit = True
            return

        if char.isprintable():
            self.input_buffer += char

    def _execute_command(self, raw: str) -> None:
        parsed = parse_shell_input(raw, self.command_verbs)
        command = parsed.verb
        payload = parsed.payload
        self.state["sessionCounter"] += 1
        append_session_event(self.root, "user", "input.command", {"raw": raw})

        if command in {"quit", "exit"}:
            self._append_log("shell", "Session sealed. Companion withdrawing from the field.")
            self.should_exit = True
            return

        if command != "send" and not self._is_command_available(command):
            self._append_log("shell", f"{command} is not available in {self.state['modeId']}.")
            return

        if command == "help":
            available = self._available_commands()
            self._append_log("shell", f"Mode {self.state['modeId']} allows {', '.join(command['verb'] for command in available)}")
            for command_manifest in available[:5]:
                self._append_log("shell", f"{command_manifest['verb']} {command_manifest['summary']}")
            return

        if command == "mode":
            if payload and payload in self.assets.modes and self._is_mode_available(payload):
                self._set_mode(payload)
            elif payload and payload in self.assets.modes:
                self._append_log("shell", f"Mode {payload} is not loaded in this shell.")
            else:
                self._append_log("shell", f"Unknown mode: {payload or '<empty>'}")
            return

        if command == "soul":
            relic = self.state["unlockedParts"].get("relic", "relic.none")
            scar = self.state["unlockedParts"].get("scar", "scar.none")
            seed = self.assets.profile["seed"]["identity"]
            self._append_log("shell", f"Seed {seed} | mode {self.state['modeId']} | tier {self.tier}")
            self._append_log(
                "shell",
                f"Relic {relic} | scar {scar} | companions {', '.join(companion['id'] for companion in self._visible_companions())}",
            )
            return

        if command == "memory":
            self.state["surfaceFocus"] = "memory"
            if not self.state["durableMemories"]:
                self._append_log("memory", "No durable memory has surfaced yet.")
                return
            previous_selection = self.state.get("selectedMemoryId")
            selected_memory = self._resolve_memory_selection(payload)
            if selected_memory is None:
                self._append_log("shell", f"No durable memory found for {payload or '<empty>'}.")
                return
            self._append_log("memory", f"{selected_memory['id']} {selected_memory['summary']}")
            self._append_log(
                "shell",
                f"{selected_memory['category']} | tags {', '.join(selected_memory['tags']) or 'none'}",
            )
            if selected_memory["id"] != previous_selection:
                self._queue_resurface_event()
            return

        if command == "inspect":
            target = payload.split()
            if len(target) >= 2 and target[0] == "memory":
                memory_id = target[1]
            elif not payload:
                selected = self._selected_memory()
                memory_id = selected["id"] if selected is not None else ""
            else:
                self._append_log("shell", "Use inspect memory <id>.")
                return
            memory = self._memory_by_id(memory_id)
            if memory is None:
                self._append_log("shell", f"No durable memory found for {memory_id or '<empty>'}.")
                return
            self.state["surfaceFocus"] = "memory"
            self.state["selectedMemoryId"] = memory["id"]
            for speaker, line in inspect_memory_lines(memory, self.state):
                self._append_log(speaker, line)
            self._queue_resurface_event()
            return

        if command == "revise":
            tokens = payload.split(maxsplit=2)
            if len(tokens) < 3 or tokens[0] != "memory":
                self._append_log("shell", "Use revise memory <id> <new text>.")
                return
            memory_id = tokens[1]
            new_text = tokens[2]
            outcome = revise_memory(self.state, memory_id, new_text)
            for speaker, line in outcome.reply_lines:
                self._append_log(speaker, line)
            for event in outcome.events:
                self._queue_event(event["kind"], event["presetId"], event["durationSeconds"])
            append_session_event(
                self.root,
                "memory",
                "memory.revise",
                {"memoryId": memory_id, "text": new_text},
            )
            return

        if command == "gallery":
            self.state["surfaceFocus"] = "gallery"
            if not self.state["artifacts"]:
                self._append_log("shell", "The gallery shelf is still dark.")
                return
            visible_artifacts = self._visible_artifacts()
            selected_artifact = self._resolve_artifact_selection(payload, visible_artifacts)
            if selected_artifact is None:
                self._append_log("shell", f"No visible artifact found for {payload or '<empty>'}.")
                return
            self._append_log("shell", f"Gallery holds {len(self.state['artifacts'])} marks.")
            source_ids = ", ".join(selected_artifact["sourceMemoryIds"]) or "seed"
            target = selected_artifact["visualBinding"]["target"]
            self._append_log("shell", f"{selected_artifact['title']} -> {target} from {source_ids}")
            return

        if command == "essence":
            self._append_log("shell", f"Theme {self.assets.theme['id']} | tier {self.tier} | cadence {self.assets.app_config['shell']['frameCadenceMs']}ms")
            self._append_log("shell", "Reference runtime exposes read-only essence for now.")
            return

        if command == "tweak":
            self._append_log("shell", "Reference tweaks are limited: use mode changes, dream, and memory shaping.")
            return

        if command == "dream":
            tokens = payload.split(maxsplit=1)
            if tokens and tokens[0] == "promote":
                draft_id = tokens[1].strip() if len(tokens) > 1 else None
                outcome = promote_dream_draft(self.state, draft_id)
                for speaker, line in outcome.reply_lines:
                    self._append_log(speaker, line)
                for event in outcome.events:
                    self._queue_event(event["kind"], event["presetId"], event["durationSeconds"])
                append_session_event(
                    self.root,
                    "memory",
                    "dream.promote",
                    {"draftId": draft_id},
                )
                return
            self._set_mode("dreaming")
            outcome = create_dream_draft(self.state, payload)
            for speaker, line in outcome.reply_lines:
                self._append_log(speaker, line)
            for event in outcome.events:
                self._queue_event(event["kind"], event["presetId"], event["durationSeconds"])
            return

        if command == "forget":
            target = payload.split()
            if len(target) == 2 and target[0] == "memory":
                outcome = forget_memory(self.state, target[1])
                for speaker, line in outcome.reply_lines:
                    self._append_log(speaker, line)
                return
            self._append_log("shell", "Use forget memory <id>.")
            return

        if parsed.explicit and command not in {"send"}:
            self._append_log("shell", f"{command} is loaded but not implemented in this reference runtime.")
            return

        if command == "send":
            message = payload
        else:
            message = raw

        self._append_log("you", message)
        append_session_event(self.root, "user", "transmission.send", {"text": message})

        outcome = remember_from_text(message, self.state)
        if outcome.reply_lines:
            for speaker, line in outcome.reply_lines:
                self._append_log(speaker, line)
            for event in outcome.events:
                self._queue_event(event["kind"], event["presetId"], event["durationSeconds"])
            if any("recovery" in memory["tags"] for memory in self.state["durableMemories"][-1:]):
                self._set_mode("recovering", quiet=True)
        else:
            self._append_log("shell", "Transmission held in session. No durable mark yet.")

    def _append_log(self, speaker: str, text: str) -> None:
        self.state["transmissionLog"].append({"speaker": speaker, "text": text})
        self.state["transmissionLog"] = self.state["transmissionLog"][-18:]

    def _queue_event(self, kind: str, preset_id: str, duration_seconds: float) -> None:
        self.transient_events.append(
            TimedEvent(kind=kind, preset_id=preset_id, expires_at=time.monotonic() + duration_seconds)
        )

    def _queue_resurface_event(self) -> None:
        self._queue_event("memory-resurfacing", "distortion.relic-phase", 0.6)

    def _prune_events(self, now: float) -> None:
        self.transient_events = [event for event in self.transient_events if event.expires_at > now]
        if self.active_transition is not None and not self.active_transition.active(now):
            self.active_transition = None

    def _build_grid(self, now: float) -> CellGrid:
        scene = self._build_scene_model(now)
        grid = CellGrid(scene.geometry.width, scene.geometry.height)

        self._draw_ambient_field(grid, scene, now)
        self._draw_seams(grid, scene, now)
        self._draw_portrait(grid, scene.geometry.portrait_origin_x, scene.geometry.portrait_origin_y, now)
        self._draw_mode_overlay(grid, scene, now)
        self._draw_companions(grid, scene.geometry.portrait_origin_x, scene.geometry.portrait_origin_y, now)
        self._draw_artifacts(grid, scene, now)
        self._draw_event_layer(grid, scene, now)
        self._draw_ui(grid, scene, now)
        self._draw_command_area(grid, scene.geometry.command_origin_y)
        self.frame_count += 1
        return grid

    def _build_scene_model(self, now: float) -> SceneModel:
        width, height = grid_dimensions()
        command_height = 3
        content_height = height - command_height
        left_width = max(34, min(42, width // 3))
        seam_x = left_width
        portrait_origin_x = max(3, left_width // 2 - 11)
        portrait_origin_y = max(3, min(content_height - 14, 6))
        geometry = SceneGeometry(
            width=width,
            height=height,
            content_height=content_height,
            left_width=left_width,
            seam_x=seam_x,
            portrait_origin_x=portrait_origin_x,
            portrait_origin_y=portrait_origin_y,
            ui_origin_x=seam_x + 3,
            command_origin_y=content_height + 1,
        )
        return SceneModel(
            profile_id=self.assets.profile["profileId"],
            mode_id=self.state["modeId"],
            capability_tier=self.tier,
            layers=["core-silhouette", "ambient-field", "state", "event", "text-ui"],
            randomness_streams={
                "identity": f"seed:{self.assets.profile['seed']['identity']}",
                "state": f"mode:{self.state['modeId']}",
                "region": "layout:portrait-left-log-right",
                "time": f"tick:{int(now * 10)}",
            },
            active_events=[event.kind for event in self.transient_events],
            motion_budget={
                "portraitCenter": "low",
                "portraitEdges": "low",
                "ambientField": "medium",
                "ui": "none",
            },
            glitch_budget="low",
            geometry=geometry,
            notes=f"{tier_label(self.tier)} reference scene model with {len(self._visible_panels())} active panels.",
            transition=self.active_transition.to_spec(now) if self.active_transition is not None and self.active_transition.active(now) else None,
        )

    def _draw_seams(self, grid: CellGrid, scene: SceneModel, now: float) -> None:
        seam_x = scene.geometry.seam_x
        content_height = scene.geometry.content_height
        divider_char = ":" if self.frame_count % 12 < 10 else "."
        if self.active_transition is not None and self.active_transition.active(now):
            divider_char = "~" if self.active_transition.style == "distortion.dream-soft" else ":"
        for y in range(content_height):
            grid.set(seam_x, y, divider_char, "ui_muted")
        for x in range(grid.width):
            if x == seam_x:
                continue
            char = "." if self.active_transition is None else ":" if self.active_transition.active(now) else "."
            grid.set(x, content_height, char, "ui_muted")

    def _draw_ambient_field(self, grid: CellGrid, scene: SceneModel, now: float) -> None:
        mode = self.assets.modes[self.state["modeId"]]
        behavior = self.assets.ambient_behaviors[mode["ambientProfile"]]
        left_width = scene.geometry.left_width
        content_height = scene.geometry.content_height
        points = max(5, int(left_width * content_height * behavior["density"] * 0.018 * self._tier_density_scale()))
        safe_core = (
            scene.geometry.portrait_origin_x - 2,
            max(2, scene.geometry.portrait_origin_y - 1),
            scene.geometry.portrait_origin_x + 24,
            min(content_height - 3, scene.geometry.portrait_origin_y + 12),
        )

        for index in range(points):
            seed = stable_int(f"{self.assets.profile['seed']['identity']}:{behavior['id']}:{index}")
            family = pick_family(behavior["glyphFamilies"], index)
            x, y = self._ambient_point(seed, index, behavior, scene, now)
            if not self._ambient_visible(seed, behavior, now):
                continue
            if safe_core[0] <= x <= safe_core[2] and safe_core[1] <= y <= safe_core[3]:
                continue

            char = glyph_for_family(family, seed, self.tier)
            style = ambient_style_for_family(family)
            grid.set(x, y, char, style)

    def _ambient_point(
        self,
        seed: int,
        index: int,
        behavior: dict[str, Any],
        scene: SceneModel,
        now: float,
    ) -> tuple[int, int]:
        region = behavior["regionTargets"][index % len(behavior["regionTargets"])]
        base_x, base_y = self._ambient_anchor(region, scene, seed)
        simulation = behavior["simulationClass"]
        phase = (now / phase_period(seed, 6.0, 20.0)) + (seed % 17)

        if simulation == "flow-field":
            x = base_x + int(round(math.sin(phase) * (2 + seed % 3)))
            y = base_y + int(round(math.cos(phase * 0.61) * (1 + seed % 2)))
        elif simulation == "anchored-pulse":
            x = base_x + int(round(math.sin(phase) * 2))
            y = base_y + int(round(math.cos(phase) * 1))
        elif simulation == "directional-flow":
            x = base_x + int(((phase * 3) % 7) - 3)
            y = base_y + int(round(math.sin(phase * 0.4) * 2))
        elif simulation == "residue-drift":
            x = base_x + int(round(math.sin(phase * 0.7) * 2))
            y = base_y - int((phase * 1.8) % 4)
        elif simulation == "stitched-return":
            x = base_x + (-1 if index % 2 == 0 else 1)
            y = base_y + int(round(math.sin(phase * 0.5)))
        elif simulation == "vector-lane":
            x = base_x + int((phase * 4) % 6) - 3
            y = base_y + int((phase * 2) % 4) - 2
        elif simulation == "beacon-scan":
            x = base_x
            y = base_y + int(round(math.sin(phase) * 3))
        elif simulation == "held-stillness":
            x = base_x + (1 if math.sin(phase) > 0.94 else 0)
            y = base_y
        else:
            x = base_x
            y = base_y

        return (
            clamp(x, 1, scene.geometry.left_width - 2),
            clamp(y, 1, scene.geometry.content_height - 2),
        )

    def _ambient_anchor(self, region: str, scene: SceneModel, seed: int) -> tuple[int, int]:
        left_width = scene.geometry.left_width
        content_height = scene.geometry.content_height
        portrait_left = scene.geometry.portrait_origin_x
        portrait_top = scene.geometry.portrait_origin_y
        portrait_right = portrait_left + 22
        portrait_bottom = portrait_top + 10

        if region == "negative-space":
            return (
                2 + (seed % max(8, left_width - 4)),
                1 + ((seed // 7) % max(6, content_height - 3)),
            )
        if region == "portrait-edge":
            perimeter = [
                (portrait_left - 2, portrait_top + 1 + (seed % 8)),
                (portrait_right + 2, portrait_top + 1 + (seed % 8)),
                (portrait_left + 2 + (seed % 16), portrait_top - 1),
                (portrait_left + 2 + (seed % 16), portrait_bottom + 1),
            ]
            return perimeter[seed % len(perimeter)]
        if region == "panel-seams":
            return (scene.geometry.seam_x - 1, 2 + (seed % max(8, content_height - 4)))
        if region == "mid-field":
            return (left_width // 2 + ((seed % 11) - 5), 4 + (seed % max(8, content_height - 8)))
        if region == "halo-lane":
            return (portrait_left + 5 + (seed % 10), max(1, portrait_top - 2))
        if region == "memory-surface":
            return (3 + (seed % max(8, left_width - 8)), max(2, content_height - 8 + (seed % 3)))
        if region == "panel-edge":
            return (scene.geometry.seam_x - 2 - (seed % 3), 2 + (seed % max(8, content_height - 4)))
        if region == "far-field":
            return (2 + (seed % 8), 1 + (seed % 6))
        return (2 + (seed % max(8, left_width - 4)), 1 + ((seed // 11) % max(6, content_height - 3)))

    def _draw_portrait(self, grid: CellGrid, origin_x: int, origin_y: int, now: float) -> None:
        active_parts = self._active_parts()
        draw_order = ["halo", "head", "eyes", "shoulders", "core", "scar", "relic"]

        for slot in draw_order:
            part_id = active_parts[slot]
            part = self.assets.portrait_parts[part_id]
            state_profile = part["stateProfiles"].get(self.state["modeId"]) or part["stateProfiles"].get("standby")
            frame_id = state_profile["frameId"]
            animation_id = state_profile["animation"]
            lines = self._frame_lines(part, frame_id, animation_id, now)
            offset_x, offset_y = self._part_offset(slot, animation_id, now)
            style = PART_STYLE.get(part["paletteRole"], "structural")
            grid.overlay_lines(origin_x + offset_x, origin_y + offset_y, lines, style)

    def _draw_companions(self, grid: CellGrid, origin_x: int, origin_y: int, now: float) -> None:
        for index, companion in enumerate(self._visible_companions()):
            seed = stable_int(f"{self.assets.profile['seed']['identity']}:{companion['id']}")
            x, y = self._companion_position(companion, index, origin_x, origin_y, now, seed)
            family = self._companion_family(companion, seed)
            char = glyph_for_family(family, seed, self.tier)
            style = ambient_style_for_family(family)
            grid.set(x, y, char, style)

    def _draw_mode_overlay(self, grid: CellGrid, scene: SceneModel, now: float) -> None:
        origin_x = scene.geometry.portrait_origin_x
        origin_y = scene.geometry.portrait_origin_y
        center_x = origin_x + 11
        mode_id = self.state["modeId"]
        phase = now / 3.2

        if mode_id == "building":
            pulse = "+" if math.sin(phase) > 0 else ":"
            grid.set(origin_x + 4, origin_y + 5, "/", "signal")
            grid.set(origin_x + 18, origin_y + 5, "\\", "signal")
            grid.set(origin_x + 6, origin_y + 7, pulse, "symbolic")
            grid.set(origin_x + 16, origin_y + 7, pulse, "symbolic")
            grid.set(center_x, origin_y + 10, pulse, "symbolic")
        elif mode_id == "researching":
            probe = "o" if math.sin(phase * 0.7) > 0.35 else "."
            grid.set(center_x, max(1, origin_y - 2), probe, "symbolic")
            grid.set(center_x, max(1, origin_y - 1), ":", "signal")
            grid.set(center_x, origin_y, ":", "signal")
            grid.set(origin_x + 2, origin_y + 2, ".", "signal")
            grid.set(origin_x + 20, origin_y + 2, ".", "signal")
            if math.sin(phase * 0.4) > 0.1:
                grid.set(origin_x + 1, origin_y + 4, ":", "ui_muted")
                grid.set(origin_x + 21, origin_y + 4, ":", "ui_muted")

    def _draw_artifacts(self, grid: CellGrid, scene: SceneModel, now: float) -> None:
        timeline_artifacts = [artifact for artifact in self._visible_artifacts() if artifact["type"] == "artifact.timeline.marker"]
        orbit_artifacts = [artifact for artifact in self._visible_artifacts() if artifact["type"] == "artifact.orbit.fragment"]

        for index, artifact in enumerate(timeline_artifacts):
            self._draw_timeline_marker(grid, scene, artifact, index, now)

        for index, artifact in enumerate(orbit_artifacts):
            self._draw_orbit_fragment(grid, scene, artifact, index, now)

    def _draw_timeline_marker(
        self,
        grid: CellGrid,
        scene: SceneModel,
        artifact: dict[str, Any],
        index: int,
        now: float,
    ) -> None:
        seed = stable_int(f"{self.assets.profile['seed']['identity']}:{artifact['id']}")
        x = max(1, scene.geometry.seam_x - 2 - (index % 2))
        anchor_y = scene.geometry.content_height - 10 - (index * 2)
        y = clamp(anchor_y, 2, scene.geometry.content_height - 4)
        tick = glyph_for_family("symbolic", seed, self.tier)
        lane = ":" if self.frame_count % 16 < 13 else "."
        grid.set(x, y, tick, "symbolic")
        grid.set(x, y + 1, lane, "ui_muted")
        if self.tier != "pure-text":
            grid.set(x + 1, y, FRAME_CHARSETS[self.tier]["horizontal"], "signal")

    def _draw_orbit_fragment(
        self,
        grid: CellGrid,
        scene: SceneModel,
        artifact: dict[str, Any],
        index: int,
        now: float,
    ) -> None:
        seed = stable_int(f"{self.assets.profile['seed']['identity']}:{artifact['id']}")
        center_x = scene.geometry.portrait_origin_x + 11
        center_y = scene.geometry.portrait_origin_y + 5
        phase = now / phase_period(seed, 7.0, 18.0) + (index * 2.1)
        radius_x = 13 + (seed % 2)
        radius_y = 6 + (seed % 2)
        x = center_x + int(round(math.cos(phase * 0.58) * radius_x))
        y = center_y + int(round(math.sin(phase * 0.46) * radius_y))
        glyph = glyph_for_family("symbolic", seed + 11, self.tier)
        grid.set(clamp(x, 1, scene.geometry.left_width - 2), clamp(y, 1, scene.geometry.content_height - 2), glyph, "symbolic")
        if math.sin(phase) > 0.65:
            trail_x = center_x + int(round(math.cos((phase - 0.35) * 0.58) * (radius_x - 1)))
            trail_y = center_y + int(round(math.sin((phase - 0.35) * 0.46) * radius_y))
            grid.set(clamp(trail_x, 1, scene.geometry.left_width - 2), clamp(trail_y, 1, scene.geometry.content_height - 2), ".", "signal")

    def _draw_event_layer(self, grid: CellGrid, scene: SceneModel, now: float) -> None:
        origin_x = scene.geometry.portrait_origin_x
        origin_y = scene.geometry.portrait_origin_y
        if not self.transient_events:
            if self.active_transition is None or not self.active_transition.active(now):
                return

        for event in self.transient_events:
            chars = self._distortion_chars(event.preset_id, 3)
            if event.kind == "artifact-reveal":
                points = [
                    (origin_x + 20, origin_y + 2),
                    (origin_x + 22, origin_y + 4),
                    (origin_x + 19, origin_y + 6),
                ]
                for (x, y), char in zip(points, chars, strict=True):
                    if int(now * 10) % 2 == 0:
                        grid.set(x, y, char, "symbolic")
            elif event.kind == "dream-shift":
                for dx in range(7, 16, 2):
                    grid.set(origin_x + dx, origin_y + 1, chars[dx % len(chars)], "signal")
                for dx in range(4, 19, 4):
                    grid.set(origin_x + dx, origin_y + 11, chars[(dx + 1) % len(chars)], "signal")
            elif event.kind == "recovery-mark":
                for dx in range(16, 20):
                    glyph = chars[0] if dx % 2 == 0 else "|"
                    grid.set(origin_x + dx, origin_y + 4, glyph, "decay")

        if self.active_transition is not None and self.active_transition.active(now):
            chars = self._distortion_chars(self.active_transition.style, 5)
            progress = self.active_transition.progress(now)
            y = max(1, origin_y - 2)
            for offset, x in enumerate(range(origin_x + 2, origin_x + 21, 4)):
                if progress < 1:
                    grid.set(x, y, chars[offset % len(chars)], "signal" if "dream" in self.active_transition.style else "ui_muted")

    def _draw_ui(self, grid: CellGrid, scene: SceneModel, now: float) -> None:
        mode = self.assets.modes[self.state["modeId"]]
        distortion = self._active_distortion_profile()
        visible_companions = self._visible_companions()
        visible_artifacts = self._visible_artifacts()
        companion_count = len(visible_companions)
        memory_count = len(self.state["durableMemories"])
        artifact_titles = ", ".join(artifact["title"] for artifact in visible_artifacts[-2:]) or "none"
        active_event = self.transient_events[-1].kind if self.transient_events else "stable"
        panel_layouts = self._panel_layouts(scene)

        for panel in self._visible_panels():
            x, y, width, height = panel_layouts[panel["zone"]]
            content_x = x + 2
            content_y = y + 1
            content_width = max(12, width - 4)
            content_height = max(1, height - 2)
            self._draw_panel_frame(grid, x, y, width, height, self._panel_title(panel))
            if panel["id"] == "panel.status.core":
                grid.write(content_x, content_y, summarize(f"{self.assets.profile['displayName'].upper()}  mode {mode['label'].lower()}", content_width), "ui_bright")
                grid.write(content_x, content_y + 1, summarize(f"ambient {mode['ambientProfile'].replace('ambient.', '')}", content_width), "ui_muted")
                grid.write(content_x + max(16, content_width // 2), content_y + 1, summarize(f"tier {self.tier}", max(8, content_width // 2 - 1)), "ui_muted")
                grid.write(content_x, content_y + 2, summarize(f"memories {memory_count}  artifacts {len(visible_artifacts)}  companions {companion_count}", content_width), "ui_muted")
                grid.write(content_x, content_y + 3, summarize(f"distortion {distortion.replace('distortion.', '')}  event {active_event}", content_width), "ui_muted")
                if scene.transition is not None:
                    transition_text = f"{scene.transition['sourceModeId']} -> {scene.transition['targetModeId']}"
                    grid.write(content_x, content_y + 4, summarize(f"transition {transition_text}", content_width), "signal")
            elif panel["id"] == "panel.transmission.log":
                log_y = content_y
                for entry in self.state["transmissionLog"][-8:]:
                    prefix = speaker_prefix(entry["speaker"])
                    wrapped = wrap(f"{prefix} {entry['text']}", content_width)
                    for line in wrapped[:2]:
                        if log_y >= content_y + content_height:
                            break
                        grid.write(content_x, log_y, line.ljust(content_width)[:content_width], speaker_style(entry["speaker"]))
                        log_y += 1
                    if log_y >= content_y + content_height:
                        break
            elif panel["id"] == "panel.command.hints":
                hints = self._command_hints()
                grid.write(content_x, content_y, summarize(" | ".join(hints[:3]), content_width), "ui_muted")
                if len(hints) > 3:
                    grid.write(content_x, content_y + 1, summarize(" | ".join(hints[3:6]), content_width), "ui_muted")
            elif panel["id"] == "panel.memory.surface":
                focus = self._surface_focus()
                if focus == "gallery":
                    gallery_lines = self._gallery_surface_lines(content_width)
                    if not gallery_lines:
                        grid.write(content_x, content_y, "No gallery marks yet.", "ui_muted")
                    else:
                        for index, line in enumerate(gallery_lines[:content_height]):
                            grid.write(content_x, content_y + index, summarize(line, content_width), "symbolic" if index == 0 else "ui_muted")
                elif focus == "dream" and self.state["dreamDrafts"]:
                    for index, line in enumerate(self._dream_surface_lines(content_width)[:content_height]):
                        grid.write(content_x, content_y + index, summarize(line, content_width), "signal" if index == 0 else "ui_muted")
                elif self.state["durableMemories"]:
                    memory_lines = self._memory_surface_lines(content_width)
                    for index, line in enumerate(memory_lines[:content_height]):
                        grid.write(content_x, content_y + index, summarize(line, content_width), "symbolic" if index == 0 else "ui_muted")
                else:
                    grid.write(content_x, content_y, "No durable marks yet.", "ui_muted")
            elif panel["id"] == "panel.artifact.shelf":
                if not visible_artifacts:
                    grid.write(content_x, content_y, "No active artifacts.", "ui_muted")
                    continue
                line = self._artifact_panel_line(visible_artifacts, content_width)
                grid.write(content_x, content_y, line, "symbolic")

    def _draw_command_area(self, grid: CellGrid, start_y: int) -> None:
        width = grid.width - 4
        grid.write(2, start_y, summarize(f"mode {self.state['modeId']} | help for loaded rituals | exit to seal session", width), "ui_muted")
        prompt = f"> {self.input_buffer}"
        grid.write(2, start_y + 1, prompt[:width].ljust(width), "ui_bright")

    def _part_offset(self, slot: str, animation_id: str, now: float) -> tuple[int, int]:
        seed = stable_int(f"{self.assets.profile['seed']['identity']}:{slot}:{animation_id}")
        phase = now / phase_period(seed, 4.0, 11.0) + (seed % 5)

        if animation_id in {"breathe-low", "return-steady", "weight-return"}:
            return (0, 1 if math.sin(phase) > 0.72 else 0)
        if animation_id in {"attend-lean"}:
            return (1 if math.sin(phase) > 0.6 else 0, 0)
        if animation_id in {"hover-quiet", "hover-attentive", "hold-bright"}:
            return (0, -1 if math.sin(phase) > 0.76 else 0)
        if animation_id in {"orbit-quiet", "orbit-attentive", "hold-near", "glow-soft"}:
            path = [(0, 0), (1, 0), (1, 1), (0, 1), (-1, 0), (0, -1)]
            return path[int((phase * 1.7) % len(path))]
        return (0, 0)

    def _frame_lines(self, part: dict[str, Any], frame_id: str, animation_id: str, now: float) -> list[str]:
        frame = next(frame for frame in part["frames"] if frame["id"] == frame_id)
        lines = list(frame["lines"])
        seed = stable_int(f"{self.assets.profile['seed']['identity']}:{part['id']}:{animation_id}")
        phase = now / phase_period(seed, 2.5, 8.0) + (seed % 11)

        if animation_id == "eye-flicker-rare" and math.sin(phase * 0.37) > 0.96:
            lines = replace_chars(lines, {"-": ".", "=": ".", "~": "."})
        elif animation_id == "open-soft":
            lines = replace_chars(lines, {"-": "~"})
        elif animation_id in {"pressure-pulse", "forge-pulse", "tight-pulse"} and math.sin(phase) > 0.0:
            lines = replace_chars(lines, {"+": "#", "O": "o"})
        elif animation_id in {"pulse-slow", "pulse-return"} and math.sin(phase) > 0.15:
            lines = replace_chars(lines, {"+": "*", "o": "O"})
        elif animation_id in {"blur-drift", "soft-drift", "blur-quiet", "echo-pulse"} and math.sin(phase) > 0.3:
            lines = replace_chars(lines, {"~": ",", "o": ".", "O": "o"})
        elif animation_id == "scan-sweep":
            lines = pulse_scan(lines, phase)
        elif animation_id == "scan-tight":
            lines = pulse_scan(lines, phase, tight=True)
        return lines

    def _active_parts(self) -> dict[str, str]:
        active_parts = dict(self.assets.portrait_pack["defaults"])
        active_parts.update(self.state["unlockedParts"])
        return active_parts

    def _active_distortion_profile(self) -> str:
        if self.transient_events:
            return self.transient_events[-1].preset_id
        return "distortion.clear"

    def _set_mode(self, mode_id: str, *, quiet: bool = False) -> None:
        previous_mode = self.state["modeId"]
        self.state["modeId"] = mode_id
        append_session_event(self.root, "mind", "mode.change", {"modeId": mode_id})
        if not quiet:
            self._append_log("shell", f"Mode shifted to {mode_id}.")
        if mode_id == "dreaming":
            self._queue_event("dream-shift", "distortion.dream-soft", 1.1)
            self._start_transition(previous_mode, mode_id, "distortion.dream-soft", 1.1)
        elif previous_mode != mode_id:
            self._start_transition(previous_mode, mode_id, "distortion.breath", 0.55)

    def _ensure_reference_relic(self) -> None:
        if "relic" in self.state["unlockedParts"]:
            return
        self.state["unlockedParts"]["relic"] = "relic.archive-lantern"
        if not any(artifact["type"] == "artifact.relic.archive-lantern" for artifact in self.state["artifacts"]):
            self.state["artifacts"].append(
                {
                    "id": "artifact_demo_0001",
                    "type": "artifact.relic.archive-lantern",
                    "title": "Archive Lantern",
                    "sourceMemoryIds": [],
                    "visualBinding": {"target": "relic", "partId": "relic.archive-lantern"},
                    "displayRules": {"visibility": "contextual", "modes": ["standby", "listening", "focused"]},
                    "stateEffects": ["portrait:unlock-relic"],
                }
            )
        if "entity.lantern-mote" not in self.state["companions"]:
            self.state["companions"].append("entity.lantern-mote")

    def _save_state(self) -> None:
        save_runtime_state(self.root, self.state)

    def _start_transition(
        self,
        source_mode_id: str,
        target_mode_id: str,
        style: str,
        duration_seconds: float,
    ) -> None:
        self.active_transition = SceneTransition(
            source_mode_id=source_mode_id,
            target_mode_id=target_mode_id,
            style=style,
            started_at=time.monotonic(),
            duration_seconds=duration_seconds,
        )

    def _collect_loaded_ids(self, field_name: str) -> list[str]:
        ordered_ids: list[str] = []
        seen: set[str] = set()
        for pack in self.assets.module_packs.values():
            for item_id in pack.get(field_name, []):
                if item_id not in seen:
                    seen.add(item_id)
                    ordered_ids.append(item_id)
        return ordered_ids

    def _available_commands(self) -> list[dict[str, Any]]:
        available: list[dict[str, Any]] = []
        for command in self.loaded_commands.values():
            if self.state["modeId"] in command["availability"]:
                available.append(command)
        return sorted(available, key=lambda item: item["verb"])

    def _is_mode_available(self, mode_id: str) -> bool:
        return mode_id in self.loaded_mode_ids

    def _is_command_available(self, verb: str) -> bool:
        return any(command["verb"] == verb for command in self._available_commands())

    def _visible_panels(self) -> list[dict[str, Any]]:
        panels: list[dict[str, Any]] = []
        for panel in self.loaded_panels.values():
            if self.state["modeId"] in panel["visibleInModes"]:
                panels.append(panel)
        return panels

    def _visible_artifacts(self) -> list[dict[str, Any]]:
        artifacts: list[dict[str, Any]] = []
        for artifact in self.state["artifacts"]:
            display_rules = artifact.get("displayRules", {})
            if not display_rules:
                artifacts.append(artifact)
                continue
            visible_modes = display_rules.get("modes", [])
            if not visible_modes or self.state["modeId"] in visible_modes:
                artifacts.append(artifact)
        return artifacts

    def _surface_focus(self) -> str:
        return str(self.state.get("surfaceFocus", "memory"))

    def _surface_lines(self, width: int) -> list[str]:
        focus = self._surface_focus()
        if focus == "gallery":
            return self._gallery_surface_lines(width)
        if focus == "dream":
            return self._dream_surface_lines(width)
        return self._memory_surface_lines(width)

    def _memory_by_id(self, memory_id: str | None) -> dict[str, Any] | None:
        if not memory_id:
            return None
        return next((memory for memory in self.state["durableMemories"] if memory["id"] == memory_id), None)

    def _artifact_by_id(self, artifact_id: str | None, artifacts: list[dict[str, Any]] | None = None) -> dict[str, Any] | None:
        if not artifact_id:
            return None
        source = artifacts if artifacts is not None else self._visible_artifacts()
        return next((artifact for artifact in source if artifact["id"] == artifact_id), None)

    def _selected_memory(self) -> dict[str, Any] | None:
        selected = self._memory_by_id(self.state.get("selectedMemoryId"))
        if selected is not None:
            return selected
        if self.state["durableMemories"]:
            fallback = self.state["durableMemories"][-1]
            self.state["selectedMemoryId"] = fallback["id"]
            return fallback
        return None

    def _selected_artifact(self, artifacts: list[dict[str, Any]] | None = None) -> dict[str, Any] | None:
        visible_artifacts = artifacts if artifacts is not None else self._visible_artifacts()
        selected = self._artifact_by_id(self.state.get("selectedArtifactId"), visible_artifacts)
        if selected is not None:
            return selected
        if visible_artifacts:
            fallback = visible_artifacts[-1]
            self.state["selectedArtifactId"] = fallback["id"]
            return fallback
        return None

    def _resolve_memory_selection(self, payload: str) -> dict[str, Any] | None:
        if not self.state["durableMemories"]:
            self.state["selectedMemoryId"] = None
            return None

        choice = payload.strip()
        if not choice:
            return self._selected_memory()
        if choice in {"next", "prev"}:
            selected = self._rotate_selection(
                self.state["durableMemories"],
                self.state.get("selectedMemoryId"),
                choice,
            )
            self.state["selectedMemoryId"] = selected["id"]
            return selected

        selected = self._memory_by_id(choice)
        if selected is not None:
            self.state["selectedMemoryId"] = selected["id"]
            return selected
        return None

    def _resolve_artifact_selection(
        self,
        payload: str,
        visible_artifacts: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        if not visible_artifacts:
            self.state["selectedArtifactId"] = None
            return None

        choice = payload.strip()
        if not choice:
            return self._selected_artifact(visible_artifacts)
        if choice in {"next", "prev"}:
            selected = self._rotate_selection(
                visible_artifacts,
                self.state.get("selectedArtifactId"),
                choice,
            )
            self.state["selectedArtifactId"] = selected["id"]
            return selected

        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(visible_artifacts):
                selected = visible_artifacts[index]
                self.state["selectedArtifactId"] = selected["id"]
                return selected

        selected = self._artifact_by_id(choice, visible_artifacts)
        if selected is not None:
            self.state["selectedArtifactId"] = selected["id"]
            return selected
        return None

    def _rotate_selection(
        self,
        items: list[dict[str, Any]],
        selected_id: str | None,
        direction: str,
    ) -> dict[str, Any]:
        if not items:
            raise ValueError("Cannot rotate an empty selection list.")

        current_index = next((index for index, item in enumerate(items) if item["id"] == selected_id), len(items) - 1)
        delta = 1 if direction == "next" else -1
        return items[(current_index + delta) % len(items)]

    def _command_hints(self) -> list[str]:
        examples = {
            "send": "send <text>",
            "dream": "dream reflect recent",
            "forget": "forget memory <id>",
            "memory": "memory",
            "gallery": "gallery",
            "soul": "soul",
            "mode": "mode listening",
            "help": "help",
            "essence": "essence",
            "tweak": "tweak",
            "inspect": "inspect memory <id>",
            "revise": "revise memory <id> <text>",
        }
        hints = [examples.get(command["verb"], command["verb"]) for command in self._available_commands()]
        focus = self._surface_focus()
        if focus == "gallery" and self._visible_artifacts():
            hints = ["gallery next", "gallery prev"] + hints
        elif focus == "memory" and self.state["durableMemories"]:
            hints = ["memory next", "inspect memory"] + hints
        if self.state.get("dreamDrafts"):
            hints.append("dream promote")
        hints.append("exit")
        deduped: list[str] = []
        for hint in hints:
            if hint not in deduped:
                deduped.append(hint)
        return deduped[:6]

    def _distortion_chars(self, preset_id: str, count: int) -> list[str]:
        preset = self.assets.distortion_presets.get(preset_id, self.assets.distortion_presets["distortion.clear"])
        chars: list[str] = []
        for index in range(count):
            family = pick_family(preset["glyphFamilies"], index)
            chars.append(glyph_for_family(family, stable_int(f"{preset_id}:{index}"), self.tier))
        return chars

    def _artifact_panel_line(self, artifacts: list[dict[str, Any]], width: int) -> str:
        fragments: list[str] = []
        selected_artifact_id = self.state.get("selectedArtifactId")
        for artifact in artifacts[-2:]:
            symbol = self._artifact_symbol(artifact["type"])
            prefix = ">" if artifact["id"] == selected_artifact_id else symbol
            fragments.append(f"{prefix} {artifact['title']}")
        return summarize(" | ".join(fragments), width)

    def _gallery_surface_lines(self, width: int) -> list[str]:
        selected_artifact = self._selected_artifact()
        if selected_artifact is None:
            return []
        source_memory = self._memory_by_id(selected_artifact["sourceMemoryIds"][0] if selected_artifact["sourceMemoryIds"] else None)
        target = selected_artifact["visualBinding"]["target"]
        source = selected_artifact["sourceMemoryIds"][0] if selected_artifact["sourceMemoryIds"] else "seed"
        artifact_type = selected_artifact["type"].replace("artifact.", "")
        lines = [
            f"{self._artifact_symbol(selected_artifact['type'])} {selected_artifact['title']}",
            f"{artifact_type} -> {target}",
            f"source {source}",
        ]
        if source_memory is not None:
            lines.append(source_memory["summary"])
        return lines

    def _dream_surface_lines(self, width: int) -> list[str]:
        if not self.state["dreamDrafts"]:
            return []
        draft = self.state["dreamDrafts"][-1]
        return [summarize(line, width) for line in draft["lines"][:3]]

    def _memory_surface_lines(self, width: int) -> list[str]:
        selected_memory = self._selected_memory()
        if selected_memory is None:
            return []
        tags = ", ".join(selected_memory["tags"]) or "none"
        return [
            f"{selected_memory['id']} {selected_memory['summary']}",
            f"category {selected_memory['category']}",
            f"tags {tags}",
        ]

    def _artifact_symbol(self, artifact_type: str) -> str:
        return {
            "artifact.relic.archive-lantern": "*",
            "artifact.scar.stitched-echo": "x",
            "artifact.timeline.marker": "+",
            "artifact.gallery.card": "[]",
            "artifact.orbit.fragment": "o",
        }.get(artifact_type, "*")

    def _sync_boot_log(self) -> None:
        if not self.state["transmissionLog"]:
            self.state["transmissionLog"] = [
                {"speaker": "shell", "text": "Companion presence initialized."},
                {"speaker": "shell", "text": f"{tier_label(self.tier)} tier active. Calm holds the field."},
            ]
            return

        tier_line = f"{tier_label(self.tier)} tier active. Calm holds the field."
        known_boot_lines = {
            "Pure-text tier active. Calm holds the field.",
            "Rich-unicode tier active. Calm holds the field.",
            "Hybrid-graphics tier active. Calm holds the field.",
        }
        if len(self.state["transmissionLog"]) == 1:
            self.state["transmissionLog"].append({"speaker": "shell", "text": tier_line})
        elif self.state["transmissionLog"][1]["speaker"] == "shell" and self.state["transmissionLog"][1]["text"] in known_boot_lines:
            self.state["transmissionLog"][1]["text"] = tier_line

    def _tier_density_scale(self) -> float:
        profile = self.assets.capability_profiles.get(self.tier, {})
        unicode_level = profile.get("unicodeLevel", "conservative")
        if unicode_level == "rich":
            return 1.1
        return 0.9

    def _ambient_visible(self, seed: int, behavior: dict[str, Any], now: float) -> bool:
        cadence = behavior["cadenceWindowMs"]
        minimum = cadence["min"] / 1000.0
        maximum = cadence["max"] / 1000.0
        cycle = phase_period(seed, minimum, maximum)
        elapsed = (now + ((seed % 113) / 113.0)) % cycle
        duty = 0.28 + ((seed % 23) / 100.0)
        if behavior["simulationClass"] in {"held-stillness", "anchored-pulse"}:
            duty *= 0.75
        if behavior["simulationClass"] in {"directional-flow", "vector-lane"}:
            duty *= 1.18
        return elapsed <= cycle * min(duty, 0.72)

    def _visible_companions(self) -> list[dict[str, Any]]:
        artifact_types = {artifact["type"] for artifact in self.state["artifacts"]}
        companions: list[dict[str, Any]] = []

        for companion_id in self.loaded_companion_ids:
            companion = self.assets.companions.get(companion_id)
            if companion is None:
                continue

            explicit = companion_id in self.state["companions"]
            bound = bool(artifact_types.intersection(companion["bindToArtifactTypes"]))
            if explicit or bound:
                companions.append(companion)

        companions.sort(key=lambda item: (item["id"] not in self.state["companions"], item["id"]))
        return companions

    def _companion_family(self, companion: dict[str, Any], seed: int) -> str:
        mode_profile = companion.get("stateProfiles", {}).get(self.state["modeId"], companion["motionProfile"])
        family_seed = stable_int(f"{companion['id']}:{mode_profile}:{seed}")
        return companion["glyphFamilies"][family_seed % len(companion["glyphFamilies"])]

    def _companion_position(
        self,
        companion: dict[str, Any],
        index: int,
        origin_x: int,
        origin_y: int,
        now: float,
        seed: int,
    ) -> tuple[int, int]:
        center_x = origin_x + 11
        center_y = origin_y + 5
        lantern_x = origin_x + 22
        lantern_y = origin_y + 6
        orbit_style = companion.get("orbitStyle", "wide-calm")
        state_profile = companion.get("stateProfiles", {}).get(self.state["modeId"], companion["motionProfile"])
        radius_x, radius_y = {
            "wide-calm": (12, 5),
            "close-lantern": (7, 3),
            "inner-ring": (5, 2),
        }.get(orbit_style, (9, 4))
        phase = now / phase_period(seed, 5.0, 14.0) + (index * 1.3)

        if state_profile == "near-shoulder-hover":
            x = center_x + 7 + int(round(math.sin(phase) * 1))
            y = center_y + 2 + int(round(math.cos(phase * 0.6) * 1))
        elif state_profile == "hold-distance":
            x = center_x - radius_x - 2 + int(round(math.sin(phase * 0.4) * 1))
            y = center_y - radius_y + int(round(math.cos(phase * 0.3) * 1))
        elif state_profile in {"slow-orbit", "quiet-arc", "dim-orbit"}:
            x = center_x + int(round(math.cos(phase * 0.55) * radius_x))
            y = center_y + int(round(math.sin(phase * 0.42) * radius_y))
        elif state_profile == "echo-orbit":
            x = center_x + int(round(math.cos(phase * 0.45) * (radius_x - 1)))
            y = center_y - 1 + int(round(math.sin(phase * 0.35) * (radius_y + 1)))
        elif state_profile == "stitched-hover":
            x = center_x + 6 + int(round(math.sin(phase) * 1))
            y = center_y - 1 + int(round(math.cos(phase * 0.5) * 1))
        elif state_profile in {"float-soft", "hold-lantern"}:
            x = lantern_x + int(round(math.cos(phase * 0.8) * max(2, radius_x - 3)))
            y = lantern_y + int(round(math.sin(phase * 0.6) * max(1, radius_y)))
        else:
            x = center_x + int(round(math.cos(phase) * (radius_x - index)))
            y = center_y + int(round(math.sin(phase * 0.8) * (radius_y + index)))

        return (
            clamp(x, 1, origin_x + 27),
            clamp(y, 1, origin_y + 12),
        )

    def _panel_layouts(self, scene: SceneModel) -> dict[str, tuple[int, int, int, int]]:
        right_x = scene.geometry.ui_origin_x
        right_width = scene.geometry.width - right_x - 2
        left_x = 1
        left_width = max(20, scene.geometry.left_width - 2)
        bottom_right_y = scene.geometry.content_height - 5
        center_right_y = 8
        center_right_height = max(8, bottom_right_y - center_right_y - 1)

        return {
            "top-right": (right_x, 1, right_width, 6),
            "center-right": (right_x, center_right_y, right_width, center_right_height),
            "bottom-right": (right_x, bottom_right_y, right_width, 4),
            "lower-left": (left_x, scene.geometry.content_height - 8, left_width, 5),
            "left-accent": (left_x, scene.geometry.content_height - 3, left_width, 3),
        }

    def _panel_title(self, panel: dict[str, Any]) -> str:
        if panel["id"] == "panel.memory.surface":
            return {
                "gallery": "gallery surface",
                "dream": "dream surface",
                "memory": "memory surface",
            }.get(self._surface_focus(), "memory surface")
        return {
            "panel.status.core": "presence",
            "panel.transmission.log": "transmissions",
            "panel.command.hints": "command hints",
            "panel.artifact.shelf": "artifact shelf",
        }.get(panel["id"], panel["id"])

    def _draw_panel_frame(self, grid: CellGrid, x: int, y: int, width: int, height: int, title: str) -> None:
        if width < 8 or height < 3:
            return

        charset = FRAME_CHARSETS[self.tier]
        border_style = "signal" if self.active_transition is not None else "ui_muted"
        for dx in range(1, width - 1):
            grid.set(x + dx, y, charset["horizontal"], border_style)
            grid.set(x + dx, y + height - 1, charset["horizontal"], border_style)
        for dy in range(1, height - 1):
            grid.set(x, y + dy, charset["vertical"], border_style)
            grid.set(x + width - 1, y + dy, charset["vertical"], border_style)

        grid.set(x, y, charset["top_left"], border_style)
        grid.set(x + width - 1, y, charset["top_right"], border_style)
        grid.set(x, y + height - 1, charset["bottom_left"], border_style)
        grid.set(x + width - 1, y + height - 1, charset["bottom_right"], border_style)

        title_text = f" {summarize(title, max(4, width - 4))} "
        grid.write(x + 2, y, title_text[: max(0, width - 4)], "ui_bright")


class TerminalSession(AbstractContextManager["TerminalSession"]):
    def __init__(self, renderer: AnsiDiffRenderer, on_exit: Any) -> None:
        self.renderer = renderer
        self.on_exit = on_exit

    def __enter__(self) -> "TerminalSession":
        self.renderer.enter()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.on_exit()
        self.renderer.leave()


class InputPump(AbstractContextManager["InputPump"]):
    def __init__(self) -> None:
        self._windows = os.name == "nt"
        self._fd: int | None = None
        self._termios_settings: Any = None

    def __enter__(self) -> "InputPump":
        if not self._windows:
            import termios
            import tty

            self._fd = sys.stdin.fileno()
            self._termios_settings = termios.tcgetattr(self._fd)
            tty.setcbreak(self._fd)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if not self._windows and self._fd is not None and self._termios_settings is not None:
            import termios

            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._termios_settings)

    def read(self) -> list[str]:
        if self._windows:
            import msvcrt

            chars: list[str] = []
            while msvcrt.kbhit():
                char = msvcrt.getwch()
                if char in ("\x00", "\xe0"):
                    if msvcrt.kbhit():
                        msvcrt.getwch()
                    continue
                chars.append(char)
            return chars

        ready, _, _ = select.select([sys.stdin], [], [], 0)
        if not ready:
            return []
        return [sys.stdin.read(1)]


def detect_capability_tier(assets: RuntimeAssets, *, tier_override: str | None = None) -> str:
    if tier_override:
        if tier_override != "pure-text" and not stdout_supports_unicode():
            return "pure-text"
        return tier_override

    env_tier = os.environ.get("DREAMER2_TIER")
    if env_tier in assets.capability_profiles and (env_tier == "pure-text" or stdout_supports_unicode()):
        return env_tier

    if stdout_supports_unicode() and (os.environ.get("WT_SESSION") or os.environ.get("COLORTERM") == "truecolor"):
        return "rich-unicode"

    term = os.environ.get("TERM", "")
    if stdout_supports_unicode() and ("256color" in term or "xterm" in term):
        return "rich-unicode"

    return assets.app_config["shell"]["minimumTier"]


def grid_dimensions() -> tuple[int, int]:
    size = shutil.get_terminal_size((120, 40))
    width = max(96, size.columns)
    height = max(30, size.lines - 1)
    return (width, height)


def stdout_supports_unicode() -> bool:
    encoding = (sys.stdout.encoding or "").lower()
    return any(token in encoding for token in ("utf", "65001"))


def stable_int(value: str) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def phase_period(seed: int, minimum: float, maximum: float) -> float:
    span = maximum - minimum
    return minimum + ((seed % 997) / 997.0) * span


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


def pick_family(families: list[str], index: int) -> str:
    return families[index % len(families)]


def glyph_for_family(family: str, seed: int, tier: str) -> str:
    glyphs = list(TIER_GLYPH_OVERRIDES.get(tier, {}).get(family, GLYPH_FAMILIES[family]))
    return glyphs[seed % len(glyphs)]


def tier_label(tier: str) -> str:
    return {
        "pure-text": "Pure-text",
        "rich-unicode": "Rich-unicode",
        "hybrid-graphics": "Hybrid-graphics",
    }.get(tier, tier)


def ambient_style_for_family(family: str) -> str:
    return {
        "soft-signal": "signal",
        "dense-pressure": "structural",
        "decay": "decay",
        "symbolic": "symbolic",
        "structural": "ui_muted",
    }.get(family, "signal")


def replace_chars(lines: list[str], mapping: dict[str, str]) -> list[str]:
    return ["".join(mapping.get(char, char) for char in line) for line in lines]


def pulse_scan(lines: list[str], phase: float, *, tight: bool = False) -> list[str]:
    replacement = "=" if tight else "~"
    index = 0 if math.sin(phase) > 0 else 1
    updated: list[str] = []
    for line in lines:
        if "[" in line and "]" in line:
            sections = line.split(" ")
            signal_positions = [i for i, item in enumerate(sections) if "-" in item or "=" in item or "~" in item]
            if signal_positions:
                target = signal_positions[index % len(signal_positions)]
                sections[target] = sections[target].replace("-", replacement).replace("=", replacement)
            updated.append(" ".join(sections))
        else:
            updated.append(line)
    return updated


def speaker_prefix(speaker: str) -> str:
    return {
        "you": "you>",
        "shell": "shell>",
        "memory": "memory>",
    }.get(speaker, f"{speaker}>")


def speaker_style(speaker: str) -> str:
    return {
        "you": "ui_bright",
        "shell": "signal",
        "memory": "symbolic",
    }.get(speaker, "ui_muted")


def summarize(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."
