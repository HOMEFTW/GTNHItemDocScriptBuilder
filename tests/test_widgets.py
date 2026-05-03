import tkinter as tk
import unittest

from core.ore_dictionary_index import OreDictionaryIndexStore
from gui.widgets import FluidListFrame, FluidListRowsFrame, ItemSearchFrame, OreDictionarySearchDialog, PreviewFrame


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

    def test_multi_row_frame_returns_all_filled_fluids(self):
        frame = FluidListRowsFrame(self.root, "GT 删除流体输入", 4, lambda _target: None, lambda: None)

        frame.rows[0].name_var.set("<liquid:water>")
        frame.rows[0].amount_var.set("1000")
        frame.rows[2].name_var.set("chlorine")
        frame.rows[2].amount_var.set("144")

        fluids = frame.fluids()
        self.assertEqual(2, len(fluids))
        self.assertEqual("<liquid:water> * 1000", fluids[0].to_zs())
        self.assertEqual("<liquid:chlorine> * 144", fluids[1].to_zs())


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


class OreDictionarySearchDialogTest(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_ore_dictionary_dialog_lists_search_results(self):
        store = OreDictionaryIndexStore.from_data(
            {
                "entries": [
                    {
                        "oreName": "stickWood",
                        "ctExpression": "<ore:stickWood>",
                        "itemCount": 2,
                        "items": ["<minecraft:stick>", "<BiomesOPlenty:bamboo>"],
                        "guid": "stickWood",
                    }
                ]
            }
        )
        dialog = OreDictionarySearchDialog(self.root, store, lambda _entry: None)

        self.assertEqual("选择矿物字典", dialog.title())
        self.assertEqual(1, len(dialog.entries))
        self.assertTrue(dialog.tree.cget("yscrollcommand"))
        self.assertTrue(dialog.tree.cget("xscrollcommand"))

        dialog.destroy()


if __name__ == "__main__":
    unittest.main()
