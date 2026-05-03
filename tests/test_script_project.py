import shutil
import unittest
from pathlib import Path

from core.script_project import AppConfig, normalize_window_geometry, save_script


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
        self.assertEqual("1500x820", normalize_window_geometry("1200x820", min_width=1500, min_height=760))
        self.assertEqual("1500x760+10+20", normalize_window_geometry("900x600+10+20", min_width=1500, min_height=760))
        self.assertEqual("1600x900", normalize_window_geometry("1600x900", min_width=1500, min_height=760))

    def test_save_script_creates_parent_directory(self):
        target = self.output_dir / "scripts" / "generated.zs"
        save_script(target, "recipes.remove(<minecraft:dirt>);")
        self.assertEqual("recipes.remove(<minecraft:dirt>);", target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
