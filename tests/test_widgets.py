import tkinter as tk
import unittest

from gui.widgets import ItemSearchFrame


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


if __name__ == "__main__":
    unittest.main()
