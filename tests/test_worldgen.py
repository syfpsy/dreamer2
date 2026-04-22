import shutil
import tempfile
import unittest
from pathlib import Path

from dreamer2_ref.app import DreamerApp
from dreamer2_ref.worldgen import (
    SceneEquation,
    load_registry,
    generate_scene,
    synthesize,
    render_to_text,
)
from dreamer2_ref.worldgen.cells import GLYPH_FAMILIES
from dreamer2_ref.worldgen.synthesis import GLYPH_POOLS, STRUCTURAL_BY_TYPE


ROOT = Path(__file__).resolve().parent.parent
EQUATION_PATH = ROOT / "packs" / "world" / "scene-equations" / "signal-chapel-reverent-instability.json"


class WorldGenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load_registry(ROOT)
        cls.equation_template = SceneEquation.from_file(EQUATION_PATH)

    def _fresh_equation(self) -> SceneEquation:
        return SceneEquation.from_file(EQUATION_PATH)

    def test_registry_loads_signal_chapel_content(self) -> None:
        self.assertIn("place.signal-chapel", self.registry.archetypes)
        self.assertIn("layout.ring-sanctum", self.registry.layouts)
        self.assertIn("focal.broken-halo-terminal", self.registry.focals)
        self.assertIn("weather.slow-signal-dust", self.registry.weather)
        self.assertIn("scar.failed-memory-extraction", self.registry.scars)
        self.assertIn("palette.sacred-machine-default", self.registry.palettes)
        self.assertIn("composition.shrine", self.registry.composition_modes)
        self.assertIn("composition.walker", self.registry.composition_modes)
        for behavior_id in (
            "behavior.breath-offset",
            "behavior.core-pulse",
            "behavior.anchor-pulse",
            "behavior.flow-field-drift",
            "behavior.ghost-trail",
            "behavior.relic-phase",
        ):
            self.assertIn(behavior_id, self.registry.behaviors)

    def test_scene_equation_reproducible(self) -> None:
        equation_a = self._fresh_equation()
        equation_b = self._fresh_equation()
        scene_a = generate_scene(equation_a, self.registry)
        scene_b = generate_scene(equation_b, self.registry)
        text_a = render_to_text(synthesize(scene_a, self.registry))
        text_b = render_to_text(synthesize(scene_b, self.registry))
        self.assertEqual(text_a, text_b)

    def test_different_seed_changes_scene(self) -> None:
        equation_a = self._fresh_equation()
        equation_b = self._fresh_equation()
        equation_b.seed = "alt-seed"
        text_a = render_to_text(synthesize(generate_scene(equation_a, self.registry), self.registry))
        text_b = render_to_text(synthesize(generate_scene(equation_b, self.registry), self.registry))
        self.assertNotEqual(text_a, text_b)

    def test_scar_absent_without_memory_tag(self) -> None:
        equation = self._fresh_equation()
        scene = generate_scene(equation, self.registry, memory_tags=[])
        self.assertEqual(scene.applied_scars, [])
        # No cell should carry the scar influence tag.
        has_scar_influence = any(
            "scar.failed-memory-extraction" in cell.dominant_influences
            for row in scene.cells
            for cell in row
        )
        self.assertFalse(has_scar_influence)

    def test_scar_applied_with_matching_memory_tag(self) -> None:
        equation = self._fresh_equation()
        scene = generate_scene(
            equation,
            self.registry,
            memory_tags=["failed-extraction"],
        )
        self.assertIn("scar.failed-memory-extraction", scene.applied_scars)
        scarred_cells = [
            cell
            for row in scene.cells
            for cell in row
            if cell.active_state == "scarred"
        ]
        self.assertGreater(len(scarred_cells), 0)

    def test_focal_claims_center_of_mass(self) -> None:
        equation = self._fresh_equation()
        scene = generate_scene(equation, self.registry)
        self.assertIsNotNone(scene.focal_cell)
        cx, cy = scene.focal_cell
        self.assertEqual(cx, scene.width // 2)
        self.assertEqual(cy, scene.height // 2)
        # Center cell must be an altar carrying the focal's dominant motif.
        center = scene.cell_at(cx, cy)
        self.assertEqual(center.type, "altar")
        self.assertEqual(center.motif_tag, "motif.stepped-halo")

    def test_composition_mode_shrine_applied(self) -> None:
        equation = self._fresh_equation()
        scene = generate_scene(equation, self.registry)
        self.assertEqual(scene.companion_mode_id, "composition.shrine")

    def test_composition_mode_falls_back_when_preferred_missing(self) -> None:
        equation = self._fresh_equation()
        # composition.projection is not yet seeded as a pack, so the preferred
        # mode is missing from the registry. The resolver must skip the
        # missing preferred id and fall to the next allowed mode in biome
        # order (shrine comes before walker in the signal-chapel archetype).
        equation.composition_mode_id = "composition.projection"
        scene = generate_scene(equation, self.registry)
        self.assertEqual(scene.companion_mode_id, "composition.shrine")

    def test_composition_mode_walks_fallback_chain(self) -> None:
        # Simulate a biome that disallows shrine; shrine.fallbackModeId is
        # "composition.walker", so the resolver should walk the chain and
        # end on walker.
        archetype = self.registry.archetypes["place.signal-chapel"]
        original = list(archetype["allowedCompositionModes"])
        try:
            archetype["allowedCompositionModes"] = ["composition.walker"]
            equation = self._fresh_equation()
            equation.composition_mode_id = "composition.shrine"
            scene = generate_scene(equation, self.registry)
            self.assertEqual(scene.companion_mode_id, "composition.walker")
        finally:
            archetype["allowedCompositionModes"] = original

    def test_rendered_glyphs_obey_cell_glyph_family(self) -> None:
        equation = self._fresh_equation()
        scene = generate_scene(equation, self.registry)
        rendered = synthesize(scene, self.registry)
        structural_types = set(STRUCTURAL_BY_TYPE.keys()) - {"floor", "void"}
        for y in range(scene.height):
            for x in range(scene.width):
                cell = scene.cell_at(x, y)
                pixel = rendered[y][x]
                if pixel.glyph == " ":
                    continue
                if cell.type in structural_types:
                    self.assertIn(pixel.glyph, set(STRUCTURAL_BY_TYPE[cell.type]))
                    continue
                if cell.type == "floor":
                    if cell.active_state == "scarred" and cell.glyph_family == "structural":
                        pool = set(GLYPH_POOLS["decay"])
                    elif cell.glyph_family == "symbolic":
                        pool = set(GLYPH_POOLS["symbolic"])
                    else:
                        pool = set(GLYPH_POOLS[cell.glyph_family])
                    self.assertIn(pixel.glyph, pool)

    def test_glyph_family_enum_coverage(self) -> None:
        # Ensure every GLYPH_FAMILIES entry has a synthesis pool so
        # a future biome can safely declare any family bias.
        for family in GLYPH_FAMILIES:
            self.assertIn(family, GLYPH_POOLS)

    def test_bindings_recorded_on_scene(self) -> None:
        equation = self._fresh_equation()
        scene = generate_scene(equation, self.registry, memory_tags=["failed-extraction"])
        self.assertGreater(len(scene.bindings), 0)
        target_kinds = {binding.target for binding in scene.bindings}
        self.assertIn("focal", target_kinds)
        # With the failed-extraction scar applied, scar bindings should exist.
        self.assertIn("scar", target_kinds)


class SoulPlaceIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        for name in ("config", "content", "packs"):
            shutil.copytree(ROOT / name, self.root / name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_soul_place_writes_scene_lines(self) -> None:
        app = DreamerApp(self.root, no_color=True, tier_override="pure-text")
        before = len(app.state["transmissionLog"])
        app._execute_command("soul place")
        after = app.state["transmissionLog"]
        self.assertGreater(len(after), before)
        scene_lines = [entry for entry in after if entry["speaker"] == "scene"]
        self.assertGreater(len(scene_lines), 8)
        headers = [
            entry
            for entry in after
            if entry["speaker"] == "shell" and "place place.signal-chapel" in entry["text"]
        ]
        self.assertTrue(headers)


if __name__ == "__main__":
    unittest.main()
