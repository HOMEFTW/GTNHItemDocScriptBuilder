"""User-facing document safety and workspace regressions."""
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from gui.main_window import MainWindow


class IdeWorkflowTest(unittest.TestCase):
    def setUp(self):
        with patch.object(MainWindow, "_try_load_default_index"):
            self.window = MainWindow()
        self.addCleanup(self.window.root.destroy)

    def test_save_shortcut_works_inside_editor_and_preserves_whitespace(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "saved.zs"
            self.window._load_script_text("", path.name, path)
            text = "// 末尾空白  \n\n"
            self.window.preview.full_text.insert("1.0", text)
            self.assertTrue(self.window._document_is_dirty())
            self.assertEqual("break", self.window._shortcut_save(SimpleNamespace(widget=self.window.preview.full_text)))
            self.assertEqual(text, path.read_text(encoding="utf-8"))
            self.assertFalse(self.window._document_is_dirty())

    def test_cancel_new_preserves_document(self):
        self.window.preview.full_text.insert("1.0", "// working")
        with patch("gui.main_window.messagebox.askyesnocancel", return_value=None):
            self.window._new_script()
        self.assertEqual("// working", self.window.preview.get_full_text())

    def test_cancel_save_as_prevents_new(self):
        self.window.preview.full_text.insert("1.0", "// working")
        with patch("gui.main_window.messagebox.askyesnocancel", return_value=True), patch(
            "gui.main_window.choose_script_file", return_value=""
        ):
            self.window._new_script()
        self.assertEqual("// working", self.window.preview.get_full_text())

    def test_failed_save_prevents_document_loss(self):
        self.window._load_script_text("", "saved.zs", Path("saved.zs"))
        self.window.preview.full_text.insert("1.0", "// working")
        with patch("gui.main_window.messagebox.askyesnocancel", return_value=True), patch(
            "gui.main_window.save_script", side_effect=OSError("read only")
        ), patch("gui.main_window.show_error"):
            self.assertFalse(self.window._confirm_document_change())
        self.assertTrue(self.window._document_is_dirty())

    def test_failed_open_preserves_buffer(self):
        self.window._load_script_text("// saved", "original.zs")
        with patch("gui.main_window.show_error"), tempfile.TemporaryDirectory() as directory:
            self.window._open_script_path(Path(directory) / "missing.zs")
        self.assertEqual("// saved", self.window.preview.get_full_text())

    def test_cancel_close_keeps_window_alive(self):
        self.window.preview.full_text.insert("1.0", "// working")
        with patch("gui.main_window.messagebox.askyesnocancel", return_value=None):
            self.window._on_close()
        self.assertTrue(self.window.root.winfo_exists())

    def test_design_preview_is_visible_after_tab_switch_at_small_size(self):
        self.window.root.geometry("1000x700")
        self.window.workspace_tabs.select(self.window.design_page)
        self.window.root.update()
        self.assertTrue(self.window.preview.generated_text.winfo_ismapped())
        self.assertGreater(self.window.preview.generated_text.winfo_height(), 40)
        self.assertGreater(self.window.editor_canvas.winfo_width(), 500)

    def test_cursor_parser_infers_recipe_type(self):
        self.window._load_script_text(
            "recipes.addShapeless(<minecraft:stick>, [<minecraft:planks>]);\n"
            "furnace.setFuel(<minecraft:coal>, 1600);", "mixed.zs"
        )
        self.assertEqual(2, len(self.window.recipe_match_tree.get_children()))
        self.window.preview.full_text.mark_set(tk.INSERT, "2.4")
        self.window._edit_recipe_at_cursor()
        self.assertEqual("fuel", self.window.recipe_kind.get())
        self.assertEqual(str(self.window.design_page), self.window.workspace_tabs.select())

    def test_replace_refuses_stale_offsets(self):
        self.window._load_script_text("furnace.setFuel(<minecraft:coal>, 1600);", "fuel.zs")
        self.window._edit_recipe_at_cursor()
        self.window.preview.full_text.insert("1.0", "// inserted header\n")
        before = self.window.preview.get_full_text()
        self.window.fuel_ticks_var.set("3200")
        self.window._replace_current_recipe()
        self.assertEqual(before, self.window.preview.get_full_text())
        self.assertIn("重新解析", self.window.status_var.get())

    def test_outline_refreshes_instead_of_using_stale_offsets(self):
        self.window._load_script_text("furnace.setFuel(<minecraft:coal>, 1600);", "fuel.zs")
        self.window.preview.full_text.insert("1.0", "// header\n")
        self.window.recipe_match_tree.selection_set("0")
        self.window._parse_selected_recipe_match()
        self.assertEqual(2, self.window.recipe_matches[0].line_number)
        self.assertIn("导航已刷新", self.window.status_var.get())

    def test_disabling_parse_keeps_outline_usable(self):
        self.window._load_script_text("furnace.setFuel(<minecraft:coal>, 1600);", "fuel.zs")
        self.window._edit_recipe_at_cursor()
        self.window._disable_parse_mode()
        self.window.recipe_match_tree.selection_set("0")
        self.window._parse_selected_recipe_match()
        self.assertTrue(self.window.parse_mode_enabled.get())
        self.assertEqual("fuel", self.window.recipe_kind.get())

    def test_project_tree_opens_nested_script(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "nested").mkdir()
            target = root / "nested" / "fuel.zs"
            target.write_text("furnace.setFuel(<minecraft:coal>, 1600);", encoding="utf-8")
            (root / "ignore.txt").write_text("not a script", encoding="utf-8")
            self.window.workspace_path = root
            self.window._refresh_workspace()
            folders = self.window.project_tree.get_children()
            self.assertEqual(1, len(folders))
            script = self.window.project_tree.get_children(folders[0])[0]
            self.window.project_tree.selection_set(script)
            self.window._open_project_selection()
            self.assertEqual(target, self.window.current_script_path)

    def test_find_wraps_and_highlights_literal_text(self):
        self.window.preview.set_full_text("// alpha\n// beta alpha")
        self.window.preview.full_text.mark_set(tk.INSERT, "end-1c")
        self.window.preview.find_var.set("alpha")
        self.window.preview.find_next()
        self.assertEqual("1.3", str(self.window.preview.full_text.tag_ranges("find_match")[0]))

    def test_focused_editor_close_flushes_latest_input(self):
        self.window.preview._open_editor()
        editor = self.window.preview._editor_window
        editor.editor.insert("1.0", "// latest edit  \n\n")
        editor._close()
        self.assertEqual("// latest edit  \n\n", self.window.preview.get_full_text())
        self.assertTrue(self.window._document_is_dirty())
        self.assertFalse(self.window.preview._full_text_locked)

    def test_focused_editor_cancel_save_stays_open(self):
        self.window.preview._open_editor()
        editor = self.window.preview._editor_window
        try:
            editor.editor.insert("1.0", "// latest edit")
            with patch("gui.main_window.choose_script_file", return_value=""):
                editor._save_and_close()
            self.assertTrue(editor.winfo_exists())
            self.assertEqual("// latest edit", self.window.preview.get_full_text())
        finally:
            editor._close()

    def test_focused_editor_save_writes_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "focused.zs"
            self.window._load_script_text("", path.name, path)
            self.window.preview._open_editor()
            editor = self.window.preview._editor_window
            editor.editor.insert("1.0", "// saved  \n")
            editor._save_and_close()
            self.assertEqual("// saved  \n", path.read_text(encoding="utf-8"))
            self.assertFalse(self.window._document_is_dirty())


if __name__ == "__main__":
    unittest.main()
