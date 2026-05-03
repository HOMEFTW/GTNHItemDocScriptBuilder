import unittest

from gui.main_window import EDITOR_PANE_WEIGHT, MIN_WINDOW_SIZE, PREVIEW_PANE_WEIGHT, SEARCH_PANE_WEIGHT


class MainWindowLayoutTest(unittest.TestCase):
    def test_editor_pane_gets_primary_width(self):
        self.assertGreaterEqual(EDITOR_PANE_WEIGHT, 5)
        self.assertLess(SEARCH_PANE_WEIGHT, EDITOR_PANE_WEIGHT)
        self.assertLess(PREVIEW_PANE_WEIGHT, EDITOR_PANE_WEIGHT)

    def test_minimum_window_is_wide_enough_for_editor_controls(self):
        self.assertGreaterEqual(MIN_WINDOW_SIZE[0], 1500)
        self.assertGreaterEqual(MIN_WINDOW_SIZE[1], 760)


if __name__ == "__main__":
    unittest.main()
