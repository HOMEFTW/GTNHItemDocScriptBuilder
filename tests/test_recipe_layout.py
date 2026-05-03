import unittest

from core.recipe_layout import layout_for_kind


class RecipeLayoutTest(unittest.TestCase):
    def test_shaped_and_shapeless_use_crafting_grid(self):
        for kind in ("shaped", "shapeless"):
            layout = layout_for_kind(kind)
            self.assertEqual(9, layout.input_count)
            self.assertEqual(3, layout.input_columns)
            self.assertEqual(1, layout.output_count)
            self.assertEqual(1, layout.output_columns)

    def test_furnace_uses_one_input_and_one_output(self):
        layout = layout_for_kind("furnace")
        self.assertEqual(1, layout.input_count)
        self.assertEqual(1, layout.input_columns)
        self.assertEqual(1, layout.output_count)
        self.assertEqual(1, layout.output_columns)

    def test_machine_keeps_gt_grid(self):
        layout = layout_for_kind("machine")
        self.assertEqual(16, layout.input_count)
        self.assertEqual(4, layout.input_columns)
        self.assertEqual(4, layout.output_count)
        self.assertEqual(4, layout.output_columns)


if __name__ == "__main__":
    unittest.main()
