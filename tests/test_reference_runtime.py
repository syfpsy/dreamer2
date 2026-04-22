from __future__ import annotations

import json
import shutil
import tempfile
import threading
import unittest
from datetime import datetime
from pathlib import Path

from dreamer2_ref.app import DreamerApp
from dreamer2_ref.commands import parse_shell_input
from dreamer2_ref.web import PreviewService


class ReferenceRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        source_root = Path(__file__).resolve().parent.parent
        for name in ("config", "content", "packs"):
            shutil.copytree(source_root / name, self.root / name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_parse_shell_input_routes_unknown_text_to_send(self) -> None:
        parsed = parse_shell_input("Sketch a new ritual shell", {"send", "help", "dream"})
        self.assertEqual(parsed.verb, "send")
        self.assertEqual(parsed.payload, "Sketch a new ritual shell")
        self.assertFalse(parsed.explicit)

    def test_preference_message_unlocks_visible_relic(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("send I prefer a calm premium shell with visible continuity.")

        self.assertEqual(len(app.state["durableMemories"]), 1)
        self.assertEqual(app.state["unlockedParts"].get("relic"), "relic.archive-lantern")
        self.assertIn("entity.lantern-mote", app.state["companions"])

        render_state = app.snapshot_render_state()
        self.assertIn("artifact_0001", render_state["portrait"]["artifactBindings"])
        self.assertIn("entity.lantern-mote", render_state["portrait"]["companionBindings"])
        self.assertIn("entity.archive-shard", render_state["portrait"]["companionBindings"])

    def test_project_memory_creates_gallery_growth(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("send Our project goal is to build and ship a durable companion shell.")

        artifact_types = [artifact["type"] for artifact in app.state["artifacts"]]
        self.assertIn("artifact.timeline.marker", artifact_types)
        self.assertIn("artifact.gallery.card", artifact_types)

        render_state = app.snapshot_render_state()
        self.assertIn("entity.archive-shard", render_state["portrait"]["companionBindings"])

    def test_relationship_memory_creates_orbit_fragment(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("send This vow is important and should remain between us.")

        artifact_types = [artifact["type"] for artifact in app.state["artifacts"]]
        self.assertIn("artifact.orbit.fragment", artifact_types)

        render_state = app.snapshot_render_state()
        self.assertIn("entity.archive-shard", render_state["portrait"]["companionBindings"])

    def test_gallery_command_reports_binding_and_source(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("send Our project goal is to build and ship a durable companion shell.")
        app._execute_command("gallery")

        log_lines = [entry["text"] for entry in app.state["transmissionLog"][-4:]]
        joined = "\n".join(log_lines)
        self.assertIn("Gallery holds 2 marks.", joined)
        self.assertIn("Workshop Snapshot -> gallery from mem_0001", joined)
        self.assertEqual(app.state["surfaceFocus"], "gallery")

    def test_gallery_command_lifts_gallery_surface(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("send Our project goal is to build and ship a durable companion shell.")
        app._execute_command("gallery")

        snapshot = app.run_once()
        self.assertIn("gallery surface", snapshot)
        self.assertIn("Workshop Snapshot", snapshot)
        self.assertIn("source mem_0001", snapshot)

    def test_gallery_next_rotates_selected_artifact(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("send Our project goal is to build and ship a durable companion shell.")
        app._execute_command("gallery")
        first_selected = app.state["selectedArtifactId"]
        app._execute_command("gallery next")

        self.assertNotEqual(first_selected, app.state["selectedArtifactId"])
        snapshot = app.run_once()
        self.assertIn("Builder Mark", snapshot)
        self.assertIn("gallery next", snapshot)

    def test_visible_artifacts_follow_mode_display_rules(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("send Our project goal is to build and ship a durable companion shell.")
        app._execute_command("mode researching")

        visible_types = [artifact["type"] for artifact in app._visible_artifacts()]
        self.assertIn("artifact.gallery.card", visible_types)
        self.assertNotIn("artifact.timeline.marker", visible_types)

    def test_dream_command_creates_draft_and_sets_mode(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("send I prefer visible continuity.")
        app._execute_command("dream reflect recent")

        self.assertEqual(app.state["modeId"], "dreaming")
        self.assertTrue(app.state["dreamDrafts"])
        self.assertEqual(app.state["dreamDrafts"][-1]["prompt"], "reflect recent")
        self.assertTrue(any(event.kind == "dream-shift" for event in app.transient_events))
        self.assertIn("transition", app.snapshot_scene_model())

    def test_memory_command_selects_memory_surface_detail(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("send I prefer a calm premium shell with visible continuity.")
        app._execute_command("memory mem_0001")

        self.assertEqual(app.state["selectedMemoryId"], "mem_0001")
        snapshot = app.run_once()
        self.assertIn("memory surface", snapshot)
        self.assertIn("category long_term_personal", snapshot)

    def test_inspect_memory_surfaces_full_body_and_bindings(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("send I prefer a calm premium shell with visible continuity.")
        app._execute_command("inspect memory mem_0001")

        log_texts = [entry["text"] for entry in app.state["transmissionLog"][-6:]]
        joined = "\n".join(log_texts)
        self.assertIn("mem_0001", joined)
        self.assertIn("category long_term_personal", joined)
        self.assertIn("artifact_0001", joined)
        self.assertIn("revisions 0", joined)
        self.assertTrue(any(event.kind == "memory-resurfacing" for event in app.transient_events))

    def test_memory_selection_change_triggers_resurface_event(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("send I prefer visible continuity.")
        app._execute_command("send This vow is important and should remain between us.")
        app.transient_events.clear()

        app._execute_command("memory next")

        self.assertTrue(any(event.kind == "memory-resurfacing" for event in app.transient_events))

    def test_revise_memory_updates_summary_and_records_revision(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("send I prefer visible continuity.")
        app._execute_command("revise memory mem_0001 I prefer a calm premium continuity and a milestone vow between us.")

        memory = app.state["durableMemories"][0]
        self.assertEqual(memory["revisionCount"], 1)
        self.assertIn("milestone vow", memory["summary"])
        self.assertIn("relationship.marked", memory["tags"])
        artifact_types = [artifact["type"] for artifact in app.state["artifacts"]]
        self.assertIn("artifact.relic.archive-lantern", artifact_types)
        self.assertIn("artifact.orbit.fragment", artifact_types)
        self.assertTrue(any(event.kind == "memory-resurfacing" for event in app.transient_events))

    def test_revise_memory_reports_missing_id(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("revise memory mem_9999 rewritten body")

        self.assertIn(
            "No durable memory found for mem_9999.",
            app.state["transmissionLog"][-1]["text"],
        )

    def test_dream_promote_creates_durable_memory_with_synthesis_tag(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("send I prefer a calm premium shell with visible continuity.")
        app._execute_command("dream reflect recent")
        app._execute_command("dream promote")

        synthesis_memories = [
            memory for memory in app.state["durableMemories"]
            if "dream.synthesis" in memory.get("tags", [])
        ]
        self.assertEqual(len(synthesis_memories), 1)
        self.assertTrue(synthesis_memories[0].get("promotedFromDraftId", "").startswith("dream_"))

    def test_two_dream_promotions_produce_orbit_shard(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("send Our project goal is to build and ship a durable companion shell.")
        app._execute_command("dream reflect builder trace")
        app._execute_command("dream promote")
        app._execute_command("dream reflect second pass")
        app._execute_command("dream promote")

        orbit_artifacts = [
            artifact for artifact in app.state["artifacts"]
            if artifact["type"] == "artifact.orbit.fragment"
        ]
        self.assertTrue(orbit_artifacts)
        self.assertEqual(orbit_artifacts[-1]["title"], "Dream Shard")

    def test_forget_memory_releases_visual_marks(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("send I prefer visible continuity.")
        memory_id = app.state["durableMemories"][0]["id"]
        app._execute_command(f"forget memory {memory_id}")

        self.assertFalse(app.state["durableMemories"])
        self.assertFalse(app.state["artifacts"])
        self.assertNotIn("relic", app.state["unlockedParts"])
        self.assertNotIn("entity.lantern-mote", app.state["companions"])

    def test_scene_dump_has_expected_layer_order(self) -> None:
        app = DreamerApp(self.root, no_color=True, use_diff=True)
        scene = app.snapshot_scene_model()

        self.assertEqual(scene["capabilityTier"], "pure-text")
        self.assertEqual(
            scene["layers"],
            ["core-silhouette", "ambient-field", "state", "event", "text-ui"],
        )

    def test_work_pack_enables_building_mode(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("mode building")

        self.assertEqual(app.state["modeId"], "building")
        render_state = app.snapshot_render_state()
        self.assertEqual(render_state["ambientField"]["profile"], "ambient.tool-lane")
        self.assertNotIn("panel.command.hints", render_state["panels"])

    def test_mode_availability_blocks_unavailable_command(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("mode thinking")
        app._execute_command("memory")

        self.assertIn("memory is not available in thinking.", app.state["transmissionLog"][-1]["text"])

    def test_render_state_panels_follow_mode_visibility(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("mode dreaming")
        render_state = app.snapshot_render_state()

        self.assertIn("panel.memory.surface", render_state["panels"])
        self.assertIn("panel.artifact.shelf", render_state["panels"])
        self.assertNotIn("panel.command.hints", render_state["panels"])
        datetime.fromisoformat(render_state["timestamp"])

    def test_help_reflects_current_mode_commands(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("mode recovering")
        app._execute_command("help")

        log_lines = [entry["text"] for entry in app.state["transmissionLog"][-6:]]
        joined = "\n".join(log_lines)
        self.assertIn("Mode recovering allows", joined)
        self.assertIn("forget", joined)
        self.assertNotIn("dream", joined)

    def test_mode_not_loaded_by_module_pack_is_blocked(self) -> None:
        config_path = self.root / "config" / "defaults" / "app.config.example.json"
        with config_path.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
        config["loadedModulePacks"] = [
            "module-pack.core.rituals",
            "module-pack.archive.ledger",
        ]
        with config_path.open("w", encoding="utf-8") as handle:
            json.dump(config, handle, indent=2)

        app = DreamerApp(self.root, no_color=True)
        app._execute_command("mode building")

        self.assertEqual(app.state["modeId"], "standby")
        self.assertEqual(app.state["transmissionLog"][-1]["text"], "Mode building is not loaded in this shell.")

    def test_preview_payload_contains_grid_runs_and_theme(self) -> None:
        app = DreamerApp(self.root, no_color=True)
        app._execute_command("send I prefer a calm premium shell with visible continuity.")
        original_tier = app.tier

        payload = app.snapshot_preview_payload(tier_override="rich-unicode")

        self.assertEqual(payload["shell"]["surfaceFocus"], "gallery")
        self.assertEqual(payload["shell"]["capabilityTier"], "rich-unicode")
        self.assertEqual(app.tier, original_tier)
        self.assertEqual(payload["theme"]["id"], "theme.sacred-machine.default")
        self.assertTrue(payload["grid"]["rows"])
        self.assertIn("signature", payload["grid"]["rows"][0])
        self.assertIn("runs", payload["grid"]["rows"][0])
        self.assertIn("Archive Lantern", "\n".join(payload["shell"]["surface"]["lines"]))

    def test_preview_service_executes_command_and_limits_asset_reads(self) -> None:
        source_root = Path(__file__).resolve().parent.parent
        asset_root = source_root / "dreamer2_ref" / "web_assets"
        app = DreamerApp(self.root, no_color=True)
        service = PreviewService(app=app, asset_root=asset_root, lock=threading.Lock())

        payload = service.execute(
            "send Our project goal is to build and ship a durable companion shell.",
            "pure-text",
        )

        self.assertEqual(payload["shell"]["surfaceFocus"], "gallery")
        self.assertIn("Workshop Snapshot", "\n".join(payload["shell"]["surface"]["lines"]))
        self.assertIsNotNone(service.read_asset("index.html"))
        self.assertIsNone(service.read_asset("../README.md"))


class RuntimeStateNormalizationTests(unittest.TestCase):
    def test_existing_state_file_missing_new_keys_is_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_root = Path(__file__).resolve().parent.parent
            for name in ("config", "content", "packs"):
                shutil.copytree(source_root / name, root / name)

            state_dir = root / "state"
            state_dir.mkdir(parents=True, exist_ok=True)
            with (state_dir / "runtime_state.json").open("w", encoding="utf-8") as handle:
                json.dump(
                    {
                        "profileId": "first-light",
                        "modeId": "standby",
                        "transmissionLog": [],
                    },
                    handle,
                )

            app = DreamerApp(root, no_color=True)
            self.assertIn("dreamDrafts", app.state)
            self.assertIn("companions", app.state)
            self.assertIn("surfaceFocus", app.state)
            self.assertIn("selectedMemoryId", app.state)
            self.assertIn("selectedArtifactId", app.state)


if __name__ == "__main__":
    unittest.main()
