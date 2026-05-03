import shutil
import unittest
from pathlib import Path

from core.script_project import AppConfig, DEFAULT_WINDOW_GEOMETRY, normalize_window_geometry, save_script


class ScriptProjectTest(unittest.TestCase):
    def setUp(self):
        self.output_dir = Path("test_output")
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)

    def tearDown(self):
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)

    def test_app_config_round_trip(self):
        path = self.output_dir / "config.json"
        config = AppConfig(item_index_path="index.json", script_output_dir="scripts", last_recipe_map="gt.recipe.mixer")
        config.save(path)
        loaded = AppConfig.load(path)
        self.assertEqual("index.json", loaded.item_index_path)
        self.assertEqual("scripts", loaded.script_output_dir)
        self.assertEqual("gt.recipe.mixer", loaded.last_recipe_map)

    def test_window_geometry_is_wide_enough_for_three_panes(self):
        self.assertEqual("1500x960", normalize_window_geometry("1200x820", min_width=1500, min_height=960))
        self.assertEqual("1500x960+10+20", normalize_window_geometry("900x600+10+20", min_width=1500, min_height=960))
        self.assertEqual(
            "1600x960",
            normalize_window_geometry("1600x900", min_width=1500, min_height=960, max_width=1800),
        )

    def test_default_window_geometry_prioritizes_wide_editor(self):
        self.assertEqual("1500x1080", DEFAULT_WINDOW_GEOMETRY)
        self.assertEqual("1500x1080", normalize_window_geometry("1500x1080"))
        self.assertEqual("1500x1040+10+20", normalize_window_geometry("1200x600+10+20"))
        self.assertEqual("1500x1040", normalize_window_geometry("1700x900"))

    def test_saved_overwide_geometry_is_normalized_on_load(self):
        path = self.output_dir / "config.json"
        AppConfig(window_geometry="1700x860").save(path)

        loaded = AppConfig.load(path)

        self.assertEqual("1500x1040", loaded.window_geometry)

    def test_save_script_creates_parent_directory(self):
        target = self.output_dir / "scripts" / "generated.zs"
        save_script(target, "recipes.remove(<minecraft:dirt>);")
        self.assertEqual("recipes.remove(<minecraft:dirt>);", target.read_text(encoding="utf-8"))

    def test_pyinstaller_spec_uses_project_icon(self):
        spec_text = Path("build.spec").read_text(encoding="utf-8")
        self.assertIn('icon="icon.ico"', spec_text)
        self.assertIn('("icon.ico", ".")', spec_text)


if __name__ == "__main__":
    unittest.main()
