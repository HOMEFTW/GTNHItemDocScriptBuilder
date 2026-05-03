import tempfile
import tkinter as tk
import unittest
from pathlib import Path

from core.ore_dictionary_index import OreDictionaryEntry
from core.recipe_model import RecipeDraft, ScriptFluid, ScriptItem
from gui.dialogs import AboutDialog
from gui.main_window import (
    EDITOR_PANE_WEIGHT,
    MIN_WINDOW_SIZE,
    PREVIEW_PANE_WEIGHT,
    PREVIEW_PANE_WIDTH,
    SEARCH_PANE_WEIGHT,
    SEARCH_PANE_WIDTH,
    MainWindow,
)
import gui.main_window as main_window_module


class MainWindowLayoutTest(unittest.TestCase):
    def test_editor_pane_gets_primary_width(self):
        self.assertGreaterEqual(EDITOR_PANE_WEIGHT, 4)
        self.assertLess(SEARCH_PANE_WEIGHT, EDITOR_PANE_WEIGHT)
        self.assertLess(PREVIEW_PANE_WEIGHT, EDITOR_PANE_WEIGHT)
        self.assertEqual(580, SEARCH_PANE_WIDTH)
        self.assertLessEqual(PREVIEW_PANE_WIDTH, 420)

    def test_editor_pane_has_vertical_scrollbar(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()

            self.assertEqual("vertical", str(window.editor_vertical_scrollbar.cget("orient")))
            self.assertEqual("pack", window.editor_vertical_scrollbar.winfo_manager())
            self.assertEqual(SEARCH_PANE_WIDTH, int(window.search_frame.cget("width")))
            self.assertEqual(PREVIEW_PANE_WIDTH, int(window.preview.cget("width")))
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_minimum_window_is_wide_enough_for_editor_controls(self):
        self.assertEqual(1400, MIN_WINDOW_SIZE[0])
        self.assertGreaterEqual(MIN_WINDOW_SIZE[1], 1040)

    def test_top_lists_keep_fixed_height_when_window_gets_taller(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            window.root.update_idletasks()

            self.assertEqual(4, int(window.recipe_match_tree.cget("height")))
            self.assertEqual(3, int(window.saved_draft_tree.cget("height")))
            self.assertGreaterEqual(window.root.winfo_height(), 1040)
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_about_button_sits_on_top_right_and_opens_app_info_dialog(self):
        original_loader = MainWindow._try_load_default_index
        original_about_dialog = main_window_module.AboutDialog
        MainWindow._try_load_default_index = lambda _self: None
        opened = []

        class FakeAboutDialog:
            def __init__(self, parent):
                opened.append(parent)

        try:
            main_window_module.AboutDialog = FakeAboutDialog
            window = MainWindow()

            self.assertEqual("关于", window.about_button.cget("text"))
            self.assertEqual(window.toolbar_top, window.about_button.master)
            self.assertEqual("right", window.about_button.pack_info()["side"])

            window._show_about()

            self.assertEqual([window.root], opened)
        finally:
            MainWindow._try_load_default_index = original_loader
            main_window_module.AboutDialog = original_about_dialog
            if "window" in locals():
                window.root.destroy()

    def test_about_dialog_displays_app_version_and_studio(self):
        root = None
        dialog = None
        try:
            root = tk.Tk()
            root.withdraw()
            dialog = AboutDialog(root)

            label_texts = [
                child.cget("text")
                for child in dialog.winfo_children()[0].winfo_children()
                if hasattr(child, "cget") and child.winfo_class() == "TLabel"
            ]

            self.assertIn("GTNHItemDocScriptBuilder", label_texts)
            self.assertIn("版本 1.0.0", label_texts)
            self.assertIn("工作室 Andgatech", label_texts)
            self.assertIn("© 2026", label_texts)
        finally:
            if dialog is not None:
                dialog.destroy()
            if root is not None:
                root.destroy()

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

    def test_machine_template_selector_is_labeled_as_generation_mode(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            window.recipe_kind.set("machine")
            window._on_recipe_kind_selected()

            self.assertEqual("生成方式:", window.template_label_widget.cget("text"))
            self.assertEqual(
                (
                    "GT RA2",
                    "Thermal Expansion Furnace",
                    "Thermal Expansion Pulverizer",
                    "AE Grinder",
                    "AE Inscriber",
                ),
                window.template_combo.cget("values"),
            )
            self.assertEqual("GT RA2", window.template_label.get())
            self.assertEqual("generic_gt_machine", window.template_id.get())
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_machine_fluid_inputs_and_outputs_have_separate_dynamic_row_counts(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            window.recipe_kind.set("machine")
            window._on_recipe_kind_selected()

            self.assertEqual(1, len(window.fluid_inputs.rows))
            self.assertEqual(1, len(window.fluid_outputs.rows))
            self.assertIsNot(window.fluid_inputs.count_var, window.fluid_outputs.count_var)
            window.fluid_inputs.count_var.set("3")
            window.fluid_outputs.count_var.set("2")
            self.assertEqual(3, len(window.fluid_inputs.rows))
            self.assertEqual(2, len(window.fluid_outputs.rows))
            window.fluid_inputs.rows[0].name_var.set("<liquid:water>")
            window.fluid_inputs.rows[0].amount_var.set("1000")
            window.fluid_inputs.rows[2].name_var.set("chlorine")
            window.fluid_inputs.rows[2].amount_var.set("144")
            window.fluid_outputs.rows[0].name_var.set("steam")
            window.fluid_outputs.rows[0].amount_var.set("1000")
            window.fluid_outputs.rows[1].name_var.set("oxygen")
            window.fluid_outputs.rows[1].amount_var.set("500")
            draft = window._draft()

            self.assertEqual(2, len(draft.fluid_inputs))
            self.assertEqual(2, len(draft.fluid_outputs))
            self.assertEqual("<liquid:chlorine> * 144", draft.fluid_inputs[1].to_zs())
            self.assertEqual("<liquid:steam> * 1000", draft.fluid_outputs[0].to_zs())
            self.assertEqual("<liquid:oxygen> * 500", draft.fluid_outputs[1].to_zs())
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
            self.assertFalse(window.fluid_inputs.winfo_manager())
            self.assertEqual("pack", window.remove_fluid_inputs.winfo_manager())
            self.assertFalse(window.fluid_outputs.winfo_manager())
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_gt_remove_uses_dedicated_multi_fluid_inputs(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            window.recipe_kind.set("remove")
            window.remove_mode.set("GT")
            window._on_recipe_kind_selected()
            window.active_input_grid.slots[0].set_item(ScriptItem("<minecraft:piston>"))
            window.remove_fluid_inputs.rows[0].name_var.set("<liquid:water>")
            window.remove_fluid_inputs.rows[0].amount_var.set("1000")
            window.remove_fluid_inputs.rows[1].name_var.set("chlorine")
            window.remove_fluid_inputs.rows[1].amount_var.set("144")

            draft = window._draft()

            self.assertEqual("machine", draft.remove_mode)
            self.assertEqual(2, len(draft.fluid_inputs))
            self.assertIn("<liquid:water> * 1000", window.generator.generate(draft))
            self.assertIn("<liquid:chlorine> * 144", window.generator.generate(draft))
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_imported_gt_remove_draft_can_be_edited_again(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            draft = RecipeDraft(
                kind="remove",
                remove_mode="machine",
                recipe_map="gt.recipe.assembler",
                item_inputs=[ScriptItem("<minecraft:piston>"), ScriptItem("<ore:stickWood>")],
                fluid_inputs=[],
            )

            window._load_draft(draft)
            window.active_input_grid.slots[0].set_item(ScriptItem("<minecraft:sticky_piston>"))
            imported = window._draft()

            self.assertEqual("remove", window.recipe_kind.get())
            self.assertEqual("GT", window.remove_mode.get())
            self.assertEqual("<minecraft:sticky_piston>", imported.item_inputs[0].expression)
            self.assertIn("<minecraft:sticky_piston>", window.generator.generate(imported))
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_loaded_script_keeps_full_file_without_auto_parsing(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            script = (
                "// full file header\n"
                "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);\n"
                'mods.gregtech.RecipeRemover.remove("gt.recipe.assembler", [<minecraft:piston>], []);'
            )

            window._load_script_text(script, "test.zs")

            self.assertIn("// full file header", window.preview.get_full_text())
            self.assertIn("RecipeRemover.remove", window.preview.get_full_text())
            self.assertIn("Shaped recipe needs an output", window.preview.get_text())
            self.assertNotIn("RecipeRemover.remove", window.preview.get_text())
            self.assertIn("test.zs", window.preview.full_file_frame.cget("text"))
            self.assertIn("未解析", window.preview.generated_frame.cget("text"))
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_imported_script_waits_for_explicit_parse_and_uses_current_type(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            script = (
                "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);\n"
                "mods.gregtech.RA2\n"
                "    .builder()\n"
                "    .itemInputs([<minecraft:piston>])\n"
                "    .itemOutputs([<minecraft:bucket>])\n"
                "    .fluidInputs([])\n"
                "    .fluidOutputs([])\n"
                "    .duration(200)\n"
                "    .eut(30)\n"
                "    .addTo(\"gt.recipe.assembler\");"
            )

            window._load_script_text(script, "mixed.zs")
            self.assertEqual("shaped", window.recipe_kind.get())
            self.assertNotIn("<minecraft:stick>", window.preview.get_text())

            window.recipe_kind.set("machine")
            window._on_recipe_kind_selected()
            window._parse_current_script_to_gui()

            self.assertEqual("machine", window.recipe_kind.get())
            self.assertEqual("<minecraft:piston>", window.active_input_grid.slots[0].item.expression)
            self.assertIn("第 2 条", window.preview.generated_frame.cget("text"))
            self.assertIn("行 2", window.preview.generated_frame.cget("text"))
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_parse_mode_reparses_when_switching_script_type(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            script = (
                "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);\n"
                "mods.gregtech.RA2\n"
                "    .builder()\n"
                "    .itemInputs([<minecraft:piston>])\n"
                "    .itemOutputs([<minecraft:bucket>])\n"
                "    .fluidInputs([])\n"
                "    .fluidOutputs([])\n"
                "    .duration(200)\n"
                "    .eut(30)\n"
                "    .addTo(\"gt.recipe.assembler\");"
            )

            window._load_script_text(script, "mixed.zs")
            window.recipe_kind.set("shapeless")
            window._on_recipe_kind_selected()
            window._parse_current_script_to_gui()
            self.assertTrue(window.parse_mode_enabled.get())
            self.assertEqual("<minecraft:planks>", window.active_input_grid.slots[0].item.expression)

            window.recipe_kind.set("machine")
            window._on_recipe_kind_selected()

            self.assertEqual("machine", window.recipe_kind.get())
            self.assertEqual("<minecraft:piston>", window.active_input_grid.slots[0].item.expression)
            self.assertEqual("<minecraft:bucket>", window.active_output_grid.slots[0].item.expression)
            self.assertNotEqual("<minecraft:planks>", window.active_input_grid.slots[0].item.expression)
            self.assertIn("第 2 条", window.preview.generated_frame.cget("text"))
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_parse_navigation_buttons_move_between_matching_recipes(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            script = (
                "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);\n"
                "recipes.addShapeless(<minecraft:torch> * 4, [<minecraft:coal>, <minecraft:stick>]);\n"
                "recipes.addShapeless(<minecraft:chest>, [<minecraft:planks>]);\n"
            )

            self.assertEqual("第一条", window.first_recipe_button.cget("text"))
            self.assertEqual("上一条", window.previous_recipe_button.cget("text"))
            self.assertEqual("下一条", window.next_recipe_button.cget("text"))
            self.assertEqual("最后一条", window.last_recipe_button.cget("text"))
            window._load_script_text(script, "many.zs")
            window.recipe_kind.set("shapeless")
            window._on_recipe_kind_selected()
            window._parse_current_script_to_gui()
            self.assertEqual("<minecraft:stick>", window.active_output_grid.slots[0].item.expression)
            self.assertIn("第 1/3 条当前类型", window.preview.generated_frame.cget("text"))

            window._parse_next_recipe()
            self.assertEqual("<minecraft:torch>", window.active_output_grid.slots[0].item.expression)
            self.assertIn("第 2/3 条当前类型", window.preview.generated_frame.cget("text"))

            window._parse_last_recipe()
            self.assertEqual("<minecraft:chest>", window.active_output_grid.slots[0].item.expression)
            self.assertIn("第 3/3 条当前类型", window.preview.generated_frame.cget("text"))

            window._parse_previous_recipe()
            self.assertEqual("<minecraft:torch>", window.active_output_grid.slots[0].item.expression)
            window._parse_first_recipe()
            self.assertEqual("<minecraft:stick>", window.active_output_grid.slots[0].item.expression)
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_recipe_match_list_can_parse_selected_row(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            script = (
                "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);\n"
                "recipes.addShapeless(<minecraft:torch> * 4, [<minecraft:coal>, <minecraft:stick>]);\n"
                "recipes.addShapeless(<minecraft:chest>, [<minecraft:planks>]);\n"
            )

            self.assertEqual("配方列表", window.recipe_matches_frame.cget("text"))
            window._load_script_text(script, "many.zs")
            window.recipe_kind.set("shapeless")
            window._on_recipe_kind_selected()
            window._refresh_recipe_match_list()

            rows = window.recipe_match_tree.get_children()
            self.assertEqual(3, len(rows))
            self.assertEqual(
                ["1/3", 1, "无序合成", "<minecraft:stick> * 4 <- <minecraft:planks> * 1"],
                window.recipe_match_tree.item(rows[0])["values"],
            )
            self.assertEqual(
                ["2/3", 2, "无序合成", "<minecraft:torch> * 4 <- <minecraft:coal> * 1 和 <minecraft:stick> * 1"],
                window.recipe_match_tree.item(rows[1])["values"],
            )

            window.recipe_match_tree.selection_set(rows[1])
            window._parse_selected_recipe_match()

            self.assertEqual("<minecraft:torch>", window.active_output_grid.slots[0].item.expression)
            self.assertIn("第 2/3 条当前类型", window.preview.generated_frame.cget("text"))
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_recipe_match_summary_describes_outputs_inputs_and_recipe_map(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()

            shapeless = RecipeDraft(
                kind="shapeless",
                item_inputs=[ScriptItem("<minecraft:planks>", 2, "木板"), ScriptItem("<minecraft:coal>", 3, "煤炭")],
                item_outputs=[ScriptItem("<minecraft:torch>", 4, "火把")],
            )
            machine = RecipeDraft(
                kind="machine",
                recipe_map="gt.recipe.assembler",
                item_inputs=[ScriptItem("<minecraft:piston>", 3, "活塞"), ScriptItem("<minecraft:slime_ball>", 2, "黏液球")],
                fluid_inputs=[ScriptFluid("water", 1000, "水")],
                item_outputs=[ScriptItem("<minecraft:sticky_piston>", 1, "黏性活塞")],
                fluid_outputs=[ScriptFluid("steam", 500, "蒸汽")],
            )
            remove = RecipeDraft(kind="remove", remove_mode="all", item_outputs=[ScriptItem("<minecraft:chest>", 1, "箱子")])

            self.assertEqual(
                "火把 <minecraft:torch> * 4 <- 木板 <minecraft:planks> * 2 和 煤炭 <minecraft:coal> * 3",
                window._draft_summary(shapeless),
            )
            self.assertEqual(
                "gt.recipe.assembler: 活塞 <minecraft:piston> * 3 和 黏液球 <minecraft:slime_ball> * 2 "
                "和 水 <liquid:water> * 1000 -> 黏性活塞 <minecraft:sticky_piston> * 1 和 蒸汽 <liquid:steam> * 500",
                window._draft_summary(machine),
            )
            self.assertEqual("删除 箱子 <minecraft:chest> * 1", window._draft_summary(remove))
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_saved_draft_list_can_store_and_load_current_draft(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            window.recipe_kind.set("shapeless")
            window._on_recipe_kind_selected()
            window.active_input_grid.slots[0].set_item(ScriptItem("<minecraft:planks>", 2, "木板"))
            window.active_output_grid.slots[0].set_item(ScriptItem("<minecraft:stick>", 4, "木棍"))

            self.assertEqual("草稿列表", window.saved_drafts_frame.cget("text"))
            self.assertEqual("保存草稿", window.save_draft_button.cget("text"))
            window._save_current_draft_to_list()

            rows = window.saved_draft_tree.get_children()
            self.assertEqual(1, len(rows))
            self.assertEqual([1, "无序合成", "木棍 <minecraft:stick> * 4 <- 木板 <minecraft:planks> * 2"], window.saved_draft_tree.item(rows[0])["values"])

            window._clear_slots()
            self.assertIsNone(window.active_output_grid.slots[0].item)
            window.saved_draft_tree.selection_set(rows[0])
            window._load_selected_saved_draft()

            self.assertEqual("shapeless", window.recipe_kind.get())
            self.assertEqual("<minecraft:planks>", window.active_input_grid.slots[0].item.expression)
            self.assertEqual("<minecraft:stick>", window.active_output_grid.slots[0].item.expression)
            self.assertIn("已载入草稿 1", window.status_var.get())
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_saved_draft_list_can_delete_selected_draft(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            window.recipe_kind.set("shapeless")
            window._on_recipe_kind_selected()
            window.active_input_grid.slots[0].set_item(ScriptItem("<minecraft:planks>"))
            window.active_output_grid.slots[0].set_item(ScriptItem("<minecraft:stick>", 4))
            window._save_current_draft_to_list()
            window.active_output_grid.slots[0].set_item(ScriptItem("<minecraft:torch>", 4))
            window._save_current_draft_to_list()

            rows = window.saved_draft_tree.get_children()
            window.saved_draft_tree.selection_set(rows[0])
            window._delete_selected_saved_draft()

            rows = window.saved_draft_tree.get_children()
            self.assertEqual(1, len(rows))
            self.assertEqual([1, "无序合成", "<minecraft:torch> * 4 <- <minecraft:planks> * 1"], window.saved_draft_tree.item(rows[0])["values"])
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_saved_draft_list_can_append_all_drafts_to_full_script(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            window.preview.set_full_text("// header")
            window.recipe_kind.set("shapeless")
            window._on_recipe_kind_selected()
            window.active_input_grid.slots[0].set_item(ScriptItem("<minecraft:planks>"))
            window.active_output_grid.slots[0].set_item(ScriptItem("<minecraft:stick>", 4))
            window._save_current_draft_to_list()
            window.active_output_grid.slots[0].set_item(ScriptItem("<minecraft:torch>", 4))
            window._save_current_draft_to_list()

            self.assertEqual("全部添加", window.add_all_drafts_button.cget("text"))
            window._add_all_saved_drafts_to_script()

            full_text = window.preview.get_full_text()
            self.assertIn("// header", full_text)
            self.assertIn("recipes.addShapeless(<minecraft:stick> * 4", full_text)
            self.assertIn("recipes.addShapeless(<minecraft:torch> * 4", full_text)
            self.assertLess(full_text.index("<minecraft:stick> * 4"), full_text.index("<minecraft:torch> * 4"))
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_draft_preview_includes_auto_generated_comment(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            window.recipe_kind.set("shaped")
            window._on_recipe_kind_selected()
            window.active_input_grid.slots[0].set_item(ScriptItem("<minecraft:planks>", 2, "木板"))
            window.active_input_grid.slots[1].set_item(ScriptItem("<minecraft:coal>", 3, "煤炭"))
            window.active_output_grid.slots[0].set_item(ScriptItem("<minecraft:torch>", 1, "火把"))
            window._refresh_preview()

            self.assertTrue(
                window.preview.get_text().startswith(
                    "// 木板 <minecraft:planks> * 2 和 煤炭 <minecraft:coal> * 3 "
                    "有序合成 火把 <minecraft:torch> * 1\n"
                )
            )
            self.assertIn("recipes.addShaped", window.preview.get_text())

            window.recipe_kind.set("machine")
            window._on_recipe_kind_selected()
            window._clear_slots()
            window.active_input_grid.slots[0].set_item(ScriptItem("<minecraft:piston>", 3, "活塞"))
            window.fluid_inputs.rows[0].name_var.set("water")
            window.fluid_inputs.rows[0].amount_var.set("1000")
            window.fluid_inputs.rows[0].comment_name = "水"
            window.active_output_grid.slots[0].set_item(ScriptItem("<minecraft:sticky_piston>", 1, "黏性活塞"))
            window._refresh_preview()

            self.assertTrue(
                window.preview.get_text().startswith(
                    "// 活塞 <minecraft:piston> * 3 和 水 <liquid:water> * 1000 "
                    "通过 gt.recipe.assembler 合成 黏性活塞 <minecraft:sticky_piston> * 1\n"
                )
            )
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_disable_parse_mode_stops_auto_parse_on_type_switch(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            script = (
                "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);\n"
                "mods.gregtech.RA2.builder().itemInputs([<minecraft:piston>]).itemOutputs([<minecraft:bucket>])"
                ".fluidInputs([]).fluidOutputs([]).duration(200).eut(30).addTo(\"gt.recipe.assembler\");"
            )

            self.assertEqual("关闭解析", window.disable_parse_button.cget("text"))
            window._load_script_text(script, "mixed.zs")
            window.recipe_kind.set("shapeless")
            window._on_recipe_kind_selected()
            window._parse_current_script_to_gui()
            window._disable_parse_mode()
            window.recipe_kind.set("machine")
            window._on_recipe_kind_selected()

            self.assertFalse(window.parse_mode_enabled.get())
            self.assertIsNone(window.active_input_grid.slots[0].item)
            self.assertIn("已切换脚本类型并清空配方格", window.status_var.get())
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_manual_script_type_switch_clears_recipe_slots(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            window.recipe_kind.set("shaped")
            window._on_recipe_kind_selected()
            window.active_input_grid.slots[0].set_item(ScriptItem("<minecraft:planks>"))
            window.active_output_grid.slots[0].set_item(ScriptItem("<minecraft:stick>", 4))
            window.fluid_inputs.rows[0].name_var.set("water")

            window.recipe_kind.set("machine")
            window._on_recipe_kind_selected()

            self.assertFalse(window.parse_mode_enabled.get())
            self.assertTrue(all(slot.item is None for slot in window.active_input_grid.slots))
            self.assertTrue(all(slot.item is None for slot in window.active_output_grid.slots))
            self.assertEqual([], window.fluid_inputs.fluids())
            self.assertIn("已切换脚本类型并清空配方格", window.status_var.get())
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_window_uses_project_icon_file(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()

            self.assertEqual("icon.ico", window.app_icon_path.name)
            self.assertTrue(window.app_icon_path.exists())
            self.assertTrue(window.app_icon_configured)
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_toolbar_buttons_are_readable_and_compact(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()

            self.assertEqual("选择 item_index.json", window.choose_index_button.cget("text"))
            self.assertEqual("pack", window.toolbar_top.winfo_manager())
            self.assertEqual("pack", window.toolbar_bottom.winfo_manager())
            self.assertEqual(window.toolbar_top, window.choose_index_button.master)
            self.assertEqual(window.toolbar_bottom, window.undo_button.master)
            self.assertEqual("解析到GUI", window.parse_button.cget("text"))
            self.assertGreaterEqual(int(window.parse_button.cget("width")), 10)
            self.assertLessEqual(int(window.parse_button.cget("width")), 12)
            self.assertGreaterEqual(int(window.disable_parse_button.cget("width")), 9)
            self.assertLessEqual(int(window.add_to_script_button.cget("width")), 12)
            self.assertLessEqual(int(window.parse_button.pack_info()["padx"]), 3)
            self.assertLessEqual(int(window.disable_parse_button.pack_info()["padx"]), 3)
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_add_to_script_and_save_use_full_file_content(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            window.preview.set_full_text("// existing")
            window.recipe_kind.set("shapeless")
            window._on_recipe_kind_selected()
            window.active_input_grid.slots[0].set_item(ScriptItem("<minecraft:planks>"))
            window.active_output_grid.slots[0].set_item(ScriptItem("<minecraft:stick>", 4))

            window._add_generated_to_script()

            self.assertIn("// existing", window.preview.get_full_text())
            self.assertIn("recipes.addShapeless", window.preview.get_full_text())
            self.assertEqual(window.preview.get_full_text(), window._save_content())
            window._undo_full_script()
            self.assertEqual("// existing", window.preview.get_full_text())
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_new_script_file_creates_file_and_binds_save_path(self):
        original_loader = MainWindow._try_load_default_index
        original_choose = main_window_module.choose_script_file
        original_show_info = main_window_module.show_info
        MainWindow._try_load_default_index = lambda _self: None
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                target = Path(temp_dir) / "new_recipes.zs"
                main_window_module.choose_script_file = lambda _parent, _initial_dir="": str(target)
                main_window_module.show_info = lambda _title, _message: None
                window = MainWindow()
                window.preview.set_full_text("old text")

                self.assertEqual("新建 .zs", window.new_script_button.cget("text"))
                self.assertEqual("保存", window.save_button.cget("text"))
                self.assertEqual("另存为", window.save_as_button.cget("text"))
                window._new_script()

                self.assertTrue(target.exists())
                self.assertEqual("", target.read_text(encoding="utf-8"))
                self.assertEqual(target, window.current_script_path)
                self.assertEqual("", window.preview.get_full_text())
                self.assertIn("new_recipes.zs", window.current_script_path_var.get())
                self.assertIn("new_recipes.zs", window.preview.full_file_frame.cget("text"))
        finally:
            MainWindow._try_load_default_index = original_loader
            main_window_module.choose_script_file = original_choose
            main_window_module.show_info = original_show_info
            if "window" in locals():
                window.root.destroy()

    def test_save_uses_current_script_path_after_import_without_save_dialog(self):
        original_loader = MainWindow._try_load_default_index
        original_choose = main_window_module.choose_script_file
        original_import = main_window_module.choose_import_script_file
        original_show_info = main_window_module.show_info
        MainWindow._try_load_default_index = lambda _self: None
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                target = Path(temp_dir) / "imported.zs"
                target.write_text("// old", encoding="utf-8")
                main_window_module.choose_import_script_file = lambda _parent, _initial_dir="": str(target)
                main_window_module.choose_script_file = lambda _parent, _initial_dir="": self.fail("保存已有文件不应弹出另存为")
                main_window_module.show_info = lambda _title, _message: None
                window = MainWindow()

                window._import_script()
                window.preview.set_full_text("// changed")
                window._save_script()

                self.assertEqual("// changed", target.read_text(encoding="utf-8"))
                self.assertEqual(target, window.current_script_path)
                self.assertIn("imported.zs", window.current_script_path_var.get())
        finally:
            MainWindow._try_load_default_index = original_loader
            main_window_module.choose_script_file = original_choose
            main_window_module.choose_import_script_file = original_import
            main_window_module.show_info = original_show_info
            if "window" in locals():
                window.root.destroy()

    def test_save_without_current_path_falls_back_to_save_as(self):
        original_loader = MainWindow._try_load_default_index
        original_choose = main_window_module.choose_script_file
        original_show_info = main_window_module.show_info
        MainWindow._try_load_default_index = lambda _self: None
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                target = Path(temp_dir) / "saved_as.zs"
                main_window_module.choose_script_file = lambda _parent, _initial_dir="": str(target)
                main_window_module.show_info = lambda _title, _message: None
                window = MainWindow()
                window.preview.set_full_text("// created from blank mode")

                window._save_script()

                self.assertEqual("// created from blank mode", target.read_text(encoding="utf-8"))
                self.assertEqual(target, window.current_script_path)
                self.assertIn("saved_as.zs", window.current_script_path_var.get())
        finally:
            MainWindow._try_load_default_index = original_loader
            main_window_module.choose_script_file = original_choose
            main_window_module.show_info = original_show_info
            if "window" in locals():
                window.root.destroy()

    def test_add_to_script_can_insert_at_cursor_or_after_current_recipe(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            script = (
                "// header\n"
                "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);\n"
                "// footer"
            )
            window._load_script_text(script, "insert.zs")
            window.recipe_kind.set("shapeless")
            window._on_recipe_kind_selected()
            window._parse_current_script_to_gui()
            window.active_output_grid.slots[0].set_item(ScriptItem("<minecraft:torch>", 4))

            self.assertEqual("添加位置:", window.add_position_label_widget.cget("text"))
            self.assertEqual(("文件末尾", "当前光标", "当前配方后"), window.add_position_combo.cget("values"))
            window.add_position_var.set("当前配方后")
            window._add_generated_to_script()

            full_text = window.preview.get_full_text()
            self.assertLess(
                full_text.index("recipes.addShapeless(<minecraft:stick>"),
                full_text.index("recipes.addShapeless(<minecraft:torch>"),
            )
            self.assertLess(full_text.index("recipes.addShapeless(<minecraft:torch>"), full_text.index("// footer"))

            window.preview.set_full_text("// top\n// bottom")
            window.recipe_kind.set("shapeless")
            window._on_recipe_kind_selected()
            window.active_output_grid.slots[0].set_item(ScriptItem("<minecraft:chest>"))
            window.preview.full_text.mark_set("insert", "2.0")
            window.add_position_var.set("当前光标")
            window._add_generated_to_script()

            self.assertTrue(window.preview.get_full_text().startswith("// top\n// "))
            self.assertIn("recipes.addShapeless(<minecraft:chest>", window.preview.get_full_text())
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_add_to_script_blocks_invalid_current_draft(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            window.recipe_kind.set("shapeless")
            window._on_recipe_kind_selected()
            window.active_input_grid.slots[0].set_item(ScriptItem("<minecraft:planks>"))

            window._add_generated_to_script()

            self.assertEqual("", window.preview.get_full_text())
            self.assertTrue(window.preview.get_text().startswith("// 无法生成脚本:"))
            self.assertIn("草稿校验失败", window.status_var.get())
            self.assertIn("Shapeless recipe needs an output", window.status_var.get())
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_replace_current_recipe_blocks_invalid_current_draft(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            script = "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);"
            window._load_script_text(script, "replace.zs")
            window.recipe_kind.set("shapeless")
            window._on_recipe_kind_selected()
            window._parse_current_script_to_gui()
            window.active_output_grid.clear()

            window._replace_current_recipe()

            self.assertEqual(script, window.preview.get_full_text())
            self.assertIn("草稿校验失败", window.status_var.get())
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_invalid_machine_duration_is_reported_before_adding(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            window.recipe_kind.set("machine")
            window._on_recipe_kind_selected()
            window.active_input_grid.slots[0].set_item(ScriptItem("<minecraft:piston>"))
            window.active_output_grid.slots[0].set_item(ScriptItem("<minecraft:bucket>"))
            window.duration_var.set("abc")

            window._add_generated_to_script()

            self.assertEqual("", window.preview.get_full_text())
            self.assertIn("Duration 必须是整数", window.status_var.get())
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_replace_current_recipe_updates_original_script_block(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            script = (
                "// header\n"
                "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);\n"
                "recipes.addShapeless(<minecraft:torch> * 4, [<minecraft:coal>, <minecraft:stick>]);\n"
                "// footer"
            )
            window._load_script_text(script, "replace.zs")
            window.recipe_kind.set("shapeless")
            window._on_recipe_kind_selected()
            window._parse_next_recipe()
            window.active_output_grid.slots[0].set_item(ScriptItem("<minecraft:chest>"))

            self.assertEqual("替换原配方", window.replace_recipe_button.cget("text"))
            window._replace_current_recipe()

            full_text = window.preview.get_full_text()
            self.assertIn("// header", full_text)
            self.assertIn("recipes.addShapeless(<minecraft:stick> * 4", full_text)
            self.assertIn("recipes.addShapeless(<minecraft:chest>", full_text)
            self.assertNotIn("<minecraft:torch> * 4", full_text)
            self.assertIn("// footer", full_text)
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_full_script_undo_and_redo_buttons_edit_full_file(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            self.assertEqual("撤销", window.undo_button.cget("text"))
            self.assertEqual("重做", window.redo_button.cget("text"))
            window.preview.set_full_text("line1")
            window.preview.full_text.insert("end", "\nline2")

            window._undo_full_script()
            self.assertEqual("line1", window.preview.get_full_text())
            window._redo_full_script()
            self.assertEqual("line1\nline2", window.preview.get_full_text())
        finally:
            MainWindow._try_load_default_index = original_loader
            if "window" in locals():
                window.root.destroy()

    def test_switching_script_type_does_not_restore_hidden_old_preview(self):
        original_loader = MainWindow._try_load_default_index
        MainWindow._try_load_default_index = lambda _self: None
        try:
            window = MainWindow()
            window.recipe_kind.set("machine")
            window._on_recipe_kind_selected()
            window.active_input_grid.slots[0].set_item(ScriptItem("<minecraft:piston>"))
            window.active_output_grid.slots[0].set_item(ScriptItem("<minecraft:bucket>"))
            window._refresh_preview()
            self.assertIn("<minecraft:piston>", window.preview.get_text())

            window.recipe_kind.set("shapeless")
            window._on_recipe_kind_selected()
            window.active_input_grid.slots[0].set_item(ScriptItem("<minecraft:planks>"))
            window.active_output_grid.slots[0].set_item(ScriptItem("<minecraft:stick>", 4))
            window._refresh_preview()
            self.assertIn("<minecraft:planks>", window.preview.get_text())

            window.recipe_kind.set("machine")
            window._on_recipe_kind_selected()

            self.assertNotIn("<minecraft:piston>", window.preview.get_text())
            self.assertNotIn("<minecraft:planks>", window.preview.get_text())
            self.assertTrue(all(slot.item is None for slot in window.active_input_grid.slots))
            self.assertIn("GTNH machine template needs at least one item output", window.preview.get_text())
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
