import unittest

from core.recipe_layout import layout_key_for, layout_for_kind, remove_mode_id_from_label, remove_mode_label_options


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

    def test_fuel_uses_one_input_and_no_output(self):
        layout = layout_for_kind("fuel")
        self.assertEqual(1, layout.input_count)
        self.assertEqual(1, layout.input_columns)
        self.assertEqual(0, layout.output_count)
        self.assertEqual(1, layout.output_columns)

    def test_machine_keeps_gt_grid(self):
        layout = layout_for_kind("machine")
        self.assertEqual(16, layout.input_count)
        self.assertEqual(4, layout.input_columns)
        self.assertEqual(4, layout.output_count)
        self.assertEqual(4, layout.output_columns)

    def test_remove_sub_modes_pick_matching_layouts(self):
        self.assertEqual("remove_shaped", layout_key_for("remove", "shaped"))
        self.assertEqual("remove_shapeless", layout_key_for("remove", "shapeless"))
        self.assertEqual("remove_furnace", layout_key_for("remove", "furnace"))
        self.assertEqual("remove_machine", layout_key_for("remove", "machine"))
        self.assertEqual(9, layout_for_kind(layout_key_for("remove", "shaped")).input_count)
        self.assertEqual(1, layout_for_kind(layout_key_for("remove", "furnace")).input_count)
        self.assertEqual(16, layout_for_kind(layout_key_for("remove", "machine")).input_count)

    def test_remove_mode_labels_are_chinese_and_map_back_to_ids(self):
        labels = remove_mode_label_options()
        self.assertEqual(["有序", "无序", "熔炉", "GT"], labels)
        self.assertEqual("machine", remove_mode_id_from_label("GT"))


if __name__ == "__main__":
    unittest.main()
