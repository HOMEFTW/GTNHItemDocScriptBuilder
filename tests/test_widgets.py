import tkinter as tk
import unittest

from gui.widgets import FluidListFrame, ItemSearchFrame, PreviewFrame


class ItemSearchFrameTest(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_item_results_have_horizontal_scrollbar(self):
        frame = ItemSearchFrame(self.root, lambda _query: None, lambda _entry: None)

        self.assertTrue(frame.tree.cget("xscrollcommand"))
        self.assertEqual("horizontal", str(frame.horizontal_scrollbar.cget("orient")))


class FluidListFrameTest(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_amount_field_uses_its_own_row(self):
        frame = FluidListFrame(self.root, "流体输入", lambda _target: None, lambda: None)

        self.assertEqual(1, frame.amount_entry.grid_info()["row"])
        self.assertEqual("ew", str(frame.fluid_entry.grid_info()["sticky"]).lower())


class PreviewFrameTest(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_preview_text_has_both_scrollbars(self):
        frame = PreviewFrame(self.root)

        self.assertTrue(frame.text.cget("yscrollcommand"))
        self.assertTrue(frame.text.cget("xscrollcommand"))
        self.assertEqual("vertical", str(frame.vertical_scrollbar.cget("orient")))
        self.assertEqual("horizontal", str(frame.horizontal_scrollbar.cget("orient")))


if __name__ == "__main__":
    unittest.main()
