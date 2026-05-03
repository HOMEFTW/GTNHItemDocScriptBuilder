import unittest

from gui.main_window import (
    EDITOR_PANE_WEIGHT,
    MIN_WINDOW_SIZE,
    PREVIEW_PANE_WEIGHT,
    PREVIEW_PANE_WIDTH,
    SEARCH_PANE_WEIGHT,
    SEARCH_PANE_WIDTH,
    MainWindow,
)


class MainWindowLayoutTest(unittest.TestCase):
    def test_editor_pane_gets_primary_width(self):
        self.assertGreaterEqual(EDITOR_PANE_WEIGHT, 4)
        self.assertLess(SEARCH_PANE_WEIGHT, EDITOR_PANE_WEIGHT)
        self.assertLess(PREVIEW_PANE_WEIGHT, EDITOR_PANE_WEIGHT)
        self.assertEqual(580, SEARCH_PANE_WIDTH)
        self.assertLessEqual(PREVIEW_PANE_WIDTH, 420)

    def test_minimum_window_is_wide_enough_for_editor_controls(self):
        self.assertEqual(1400, MIN_WINDOW_SIZE[0])
        self.assertGreaterEqual(MIN_WINDOW_SIZE[1], 760)

    def test_remove_mode_shows_layout_selector(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            self.assertEqual(SEARCH_PANE_WIDTH, int(window.search_frame.cget("width")))
            self.assertEqual(PREVIEW_PANE_WIDTH, int(window.preview.cget("width")))
            window.recipe_kind.set("remove")
            window._on_recipe_kind_selected()

            self.assertEqual("删除布局:", window.remove_mode_label_widget.cget("text"))
            self.assertTrue(window.remove_mode_combo.grid_info())
            self.assertEqual(("有序", "无序", "熔炉", "GT"), window.remove_mode_combo.cget("values"))
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()


if __name__ == "__main__":
    unittest.main()
