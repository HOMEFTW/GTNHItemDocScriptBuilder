import unittest

from core.ore_dictionary_index import OreDictionaryEntry
from core.recipe_model import ScriptItem
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
        self.assertGreaterEqual(MIN_WINDOW_SIZE[1], 900)

    def test_remove_mode_shows_layout_selector(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            self.assertEqual(SEARCH_PANE_WIDTH, int(window.search_frame.cget("width")))
            self.assertEqual(PREVIEW_PANE_WIDTH, int(window.preview.cget("width")))
            self.assertFalse(window.preview.grid_propagate())
            self.assertEqual("填入 OreDict", window.ore_dictionary_button.cget("text"))
            window.recipe_kind.set("remove")
            window._on_recipe_kind_selected()

            self.assertEqual("删除布局:", window.remove_mode_label_widget.cget("text"))
            self.assertTrue(window.remove_mode_combo.grid_info())
            self.assertEqual(("有序", "无序", "熔炉", "GT"), window.remove_mode_combo.cget("values"))
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_picking_ore_dictionary_entry_fills_selected_input_slot(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            slot = window.active_input_grid.slots[0]
            window._select_slot(slot)

            window._pick_ore_dictionary(OreDictionaryEntry("stickWood", "<ore:stickWood>", 16, [], "stickWood"))

            self.assertEqual("<ore:stickWood>", slot.item.expression)
            self.assertEqual("<ore:stickWood>", slot.cget("text"))
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_selected_slot_options_apply_zero_amount_and_suffix(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            slot = window.active_input_grid.slots[0]
            slot.set_item(ScriptItem("<gregtech:gt.integrated_circuit:21>"))
            window._select_slot(slot)

            window.selected_item_amount.set("0")
            window.selected_item_suffix.set(".withTag({foo: 1})")
            window._apply_selected_item_options()

            self.assertEqual(0, slot.item.amount)
            self.assertEqual(".withTag({foo: 1})", slot.item.suffix)
            self.assertEqual("<gregtech:gt.integrated_circuit:21>.withTag({foo: 1}) * 0", slot.cget("text"))
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_no_fluid_flags_are_available_in_machine_parameters(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()

            self.assertEqual("无流体输入", window.no_fluid_inputs_checkbox.cget("text"))
            self.assertEqual("无流体输出", window.no_fluid_outputs_checkbox.cget("text"))
            window.no_fluid_inputs.set(True)
            window.no_fluid_outputs.set(True)
            draft = window._draft()

            self.assertTrue(draft.no_fluid_inputs)
            self.assertTrue(draft.no_fluid_outputs)
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_minetweaker_options_are_available_in_parameters(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()

            self.assertEqual("镜像有序合成", window.shaped_mirrored_checkbox.cget("text"))
            self.assertEqual("写入熔炉 XP", window.include_furnace_xp_checkbox.cget("text"))
            self.assertEqual("燃烧时间:", window.fuel_ticks_label_widget.cget("text"))
            self.assertEqual(0, int(window.shaped_mirrored_checkbox.grid_info()["column"]))
            window.recipe_kind.set("furnace")
            window._on_recipe_kind_selected()
            self.assertEqual(0, int(window.include_furnace_xp_checkbox.grid_info()["column"]))
            window.recipe_kind.set("fuel")
            window._on_recipe_kind_selected()
            self.assertEqual(0, int(window.fuel_ticks_label_widget.grid_info()["column"]))
            window.shaped_mirrored.set(True)
            window.include_furnace_xp.set(False)
            window.fuel_ticks_var.set("1600")
            draft = window._draft()

            self.assertTrue(draft.shaped_mirrored)
            self.assertFalse(draft.include_furnace_xp)
            self.assertEqual(1600, draft.fuel_ticks)
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_minetweaker_options_only_show_for_matching_script_type(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()

            self.assertTrue(window.shaped_mirrored_checkbox.grid_info())
            self.assertFalse(window.include_furnace_xp_checkbox.grid_info())
            self.assertFalse(window.fuel_ticks_label_widget.grid_info())

            window.recipe_kind.set("shapeless")
            window._on_recipe_kind_selected()
            self.assertFalse(window.shaped_mirrored_checkbox.grid_info())
            self.assertFalse(window.include_furnace_xp_checkbox.grid_info())
            self.assertFalse(window.fuel_ticks_label_widget.grid_info())

            window.recipe_kind.set("furnace")
            window._on_recipe_kind_selected()
            self.assertFalse(window.shaped_mirrored_checkbox.grid_info())
            self.assertTrue(window.include_furnace_xp_checkbox.grid_info())
            self.assertFalse(window.fuel_ticks_label_widget.grid_info())

            window.recipe_kind.set("fuel")
            window._on_recipe_kind_selected()
            self.assertFalse(window.shaped_mirrored_checkbox.grid_info())
            self.assertFalse(window.include_furnace_xp_checkbox.grid_info())
            self.assertTrue(window.fuel_ticks_label_widget.grid_info())
            self.assertTrue(window.fuel_ticks_entry.grid_info())
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_parameters_and_fluids_only_show_for_supported_script_type(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()

            self.assertFalse(window.template_label_widget.grid_info())
            self.assertFalse(window.recipe_map_label_widget.grid_info())
            self.assertFalse(window.fluid_inputs.winfo_manager())
            self.assertFalse(window.fluid_outputs.winfo_manager())

            window.recipe_kind.set("shapeless")
            window._on_recipe_kind_selected()
            self.assertFalse(window.fluid_inputs.winfo_manager())
            self.assertFalse(window.fluid_outputs.winfo_manager())

            window.recipe_kind.set("furnace")
            window._on_recipe_kind_selected()
            self.assertTrue(window.xp_label_widget.grid_info())
            self.assertTrue(window.xp_entry.grid_info())
            self.assertFalse(window.duration_label_widget.grid_info())
            self.assertFalse(window.fluid_inputs.winfo_manager())

            window.recipe_kind.set("fuel")
            window._on_recipe_kind_selected()
            self.assertFalse(window.xp_label_widget.grid_info())
            self.assertFalse(window.fluid_inputs.winfo_manager())

            window.recipe_kind.set("machine")
            window._on_recipe_kind_selected()
            self.assertTrue(window.template_label_widget.grid_info())
            self.assertTrue(window.recipe_map_label_widget.grid_info())
            self.assertTrue(window.duration_label_widget.grid_info())
            self.assertTrue(window.eut_label_widget.grid_info())
            self.assertEqual("pack", window.fluid_inputs.winfo_manager())
            self.assertEqual("pack", window.fluid_outputs.winfo_manager())

            window.recipe_kind.set("remove")
            window.remove_mode.set("有序")
            window._on_recipe_kind_selected()
            self.assertFalse(window.template_label_widget.grid_info())
            self.assertFalse(window.fluid_inputs.winfo_manager())

            window.remove_mode.set("GT")
            window._on_remove_mode_selected()
            self.assertTrue(window.template_label_widget.grid_info())
            self.assertTrue(window.recipe_map_label_widget.grid_info())
            self.assertEqual("pack", window.fluid_inputs.winfo_manager())
            self.assertFalse(window.fluid_outputs.winfo_manager())
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_machine_output_slot_can_edit_output_chance(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            window.recipe_kind.set("machine")
            window._on_recipe_kind_selected()
            slot = window.active_output_grid.slots[0]
            slot.set_item(ScriptItem("<minecraft:gold_nugget>"))
            window._select_slot(slot)

            self.assertEqual("输出概率:", window.output_chance_label_widget.cget("text"))
            self.assertTrue(window.output_chance_label_widget.grid_info())
            window.output_chance_var.set("2500")
            draft = window._draft()

            self.assertEqual([2500], draft.output_chances)
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_machine_parameters_can_edit_special_value(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()

            self.assertFalse(window.special_value_label_widget.grid_info())
            window.recipe_kind.set("machine")
            window._on_recipe_kind_selected()
            self.assertEqual("Special Value:", window.special_value_label_widget.cget("text"))
            self.assertTrue(window.special_value_label_widget.grid_info())
            window.special_value_var.set("42")
            draft = window._draft()

            self.assertEqual(42, draft.special_value)
            window.recipe_kind.set("remove")
            window.remove_mode.set("GT")
            window._on_recipe_kind_selected()
            self.assertFalse(window.special_value_label_widget.grid_info())
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_machine_parameters_can_fill_special_item_from_selected_slot(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()

            self.assertFalse(window.special_item_label_widget.grid_info())
            window.recipe_kind.set("machine")
            window._on_recipe_kind_selected()
            slot = window.active_input_grid.slots[0]
            slot.set_item(ScriptItem("<gregtech:gt.integrated_circuit:24>", 0, "", ".withTag({mode: 1})"))
            window._select_slot(slot)
            window._set_special_item_from_selected_slot()
            draft = window._draft()

            self.assertEqual("Special Item:", window.special_item_label_widget.cget("text"))
            self.assertTrue(window.special_item_label_widget.grid_info())
            self.assertEqual(
                "<gregtech:gt.integrated_circuit:24>.withTag({mode: 1}) * 0",
                window.special_item_var.get(),
            )
            self.assertEqual("<gregtech:gt.integrated_circuit:24>", draft.special_item.expression)
            self.assertEqual(0, draft.special_item.amount)
            self.assertEqual(".withTag({mode: 1})", draft.special_item.suffix)
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()


if __name__ == "__main__":
    unittest.main()
