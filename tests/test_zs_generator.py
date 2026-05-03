import unittest

from core.recipe_model import RecipeDraft, ScriptFluid, ScriptItem
from core.templates import (
    RECIPE_MAPS,
    recipe_map_id_from_label,
    recipe_map_label,
    recipe_map_label_options,
    template_id_from_label,
    template_label,
    template_label_options,
)
from core.zs_generator import ZsGenerator


class ZsGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.generator = ZsGenerator()

    def item(self, expression, amount=1, suffix=""):
        return ScriptItem(expression=expression, amount=amount, comment_name="", suffix=suffix)

    def test_generates_shaped_recipe(self):
        draft = RecipeDraft(
            kind="shaped",
            item_inputs=[
                self.item("<minecraft:planks>"),
                self.item("<minecraft:planks>"),
                self.item("<minecraft:planks>"),
                self.item("<minecraft:planks>"),
                None,
                self.item("<minecraft:planks>"),
                self.item("<minecraft:planks>"),
                self.item("<minecraft:planks>"),
                self.item("<minecraft:planks>"),
            ],
            item_outputs=[self.item("<minecraft:chest>")],
        )
        script = self.generator.generate(draft)
        self.assertIn("recipes.addShaped(<minecraft:chest>,", script)
        self.assertIn("[<minecraft:planks>, null, <minecraft:planks>]", script)

    def test_generates_mirrored_shaped_recipe(self):
        draft = RecipeDraft(
            kind="shaped",
            item_inputs=[
                self.item("<minecraft:planks>"),
                None,
                None,
                None,
                self.item("<minecraft:stick>"),
                None,
                None,
                None,
                self.item("<minecraft:stick>"),
            ],
            item_outputs=[self.item("<minecraft:wooden_sword>")],
            shaped_mirrored=True,
        )
        script = self.generator.generate(draft)

        self.assertIn("recipes.addShapedMirrored(<minecraft:wooden_sword>,", script)

    def test_generates_shapeless_recipe_with_amount(self):
        draft = RecipeDraft(
            kind="shapeless",
            item_inputs=[self.item("<minecraft:planks>")],
            item_outputs=[self.item("<minecraft:stick>", 4)],
        )
        self.assertEqual(
            "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);",
            self.generator.generate(draft).strip(),
        )

    def test_generates_gt_recipe_with_zero_count_input(self):
        draft = RecipeDraft(
            kind="machine",
            template_id="assembler_like",
            item_inputs=[self.item("<gregtech:gt.integrated_circuit:21>", 0)],
            item_outputs=[self.item("<minecraft:bucket>")],
            duration=200,
            eut=30,
        )
        script = self.generator.generate(draft)
        self.assertIn(".itemInputs([<gregtech:gt.integrated_circuit:21> * 0])", script)

    def test_generates_item_with_nbt_suffix_before_amount(self):
        item = self.item(
            "<appliedenergistics2:item.ItemMultiMaterial:47>",
            2,
            ".withTag({baseCapacity: 4611686018427385856 as long})",
        )

        self.assertEqual(
            "<appliedenergistics2:item.ItemMultiMaterial:47>.withTag({baseCapacity: 4611686018427385856 as long}) * 2",
            item.to_zs(),
        )

    def test_generates_furnace_recipe(self):
        draft = RecipeDraft(
            kind="furnace",
            item_inputs=[self.item("<minecraft:sand>")],
            item_outputs=[self.item("<minecraft:glass>")],
            xp=0.0,
        )
        self.assertEqual(
            "furnace.addRecipe(<minecraft:glass>, <minecraft:sand>, 0.0);",
            self.generator.generate(draft).strip(),
        )

    def test_generates_furnace_recipe_without_xp(self):
        draft = RecipeDraft(
            kind="furnace",
            item_inputs=[self.item("<minecraft:sand>")],
            item_outputs=[self.item("<minecraft:glass>")],
            include_furnace_xp=False,
        )

        self.assertEqual(
            "furnace.addRecipe(<minecraft:glass>, <minecraft:sand>);",
            self.generator.generate(draft).strip(),
        )

    def test_generates_furnace_fuel_script(self):
        draft = RecipeDraft(
            kind="fuel",
            item_inputs=[self.item("<minecraft:coal>")],
            fuel_ticks=1600,
        )

        self.assertEqual(
            "furnace.setFuel(<minecraft:coal>, 1600);",
            self.generator.generate(draft).strip(),
        )

    def test_generates_remove_recipe(self):
        draft = RecipeDraft(kind="remove", item_outputs=[self.item("<minecraft:chest>")], remove_mode="all")
        self.assertEqual("recipes.remove(<minecraft:chest>);", self.generator.generate(draft).strip())

    def test_generates_template_recipe(self):
        draft = RecipeDraft(
            kind="machine",
            template_id="thermal_expansion_furnace",
            item_inputs=[self.item("<minecraft:sand>")],
            item_outputs=[self.item("<minecraft:glass>")],
            eut=4000,
        )
        self.assertEqual(
            "mods.thermalexpansion.Furnace.addRecipe(4000, <minecraft:sand>, <minecraft:glass>);",
            self.generator.generate(draft).strip(),
        )

    def test_generates_generic_gt_machine_recipe(self):
        draft = RecipeDraft(
            kind="machine",
            template_id="assembler_like",
            item_inputs=[self.item("<minecraft:iron_ingot>")],
            item_outputs=[self.item("<minecraft:bucket>")],
            fluid_inputs=[ScriptFluid("water", 1000)],
            fluid_outputs=[],
            duration=200,
            eut=30,
        )
        script = self.generator.generate(draft)
        self.assertIn("mods.gregtech.RA2", script)
        self.assertIn(".builder()", script)
        self.assertIn(".itemInputs([<minecraft:iron_ingot>])", script)
        self.assertIn(".itemOutputs([<minecraft:bucket>])", script)
        self.assertIn(".fluidInputs([<liquid:water> * 1000])", script)
        self.assertIn('.addTo("gt.recipe.assembler");', script)
        self.assertIn("<liquid:water> * 1000", script)
        self.assertIn(".duration(200)", script)
        self.assertIn(".eut(30)", script)

    def test_generates_gt_recipe_with_explicit_no_fluid_calls(self):
        draft = RecipeDraft(
            kind="machine",
            template_id="assembler_like",
            item_inputs=[self.item("<minecraft:iron_ingot>")],
            item_outputs=[self.item("<minecraft:bucket>")],
            fluid_inputs=[ScriptFluid("water", 1000)],
            fluid_outputs=[ScriptFluid("steam", 1000)],
            no_fluid_inputs=True,
            no_fluid_outputs=True,
            duration=200,
            eut=30,
        )
        script = self.generator.generate(draft)

        self.assertIn(".noFluidInputs()", script)
        self.assertIn(".noFluidOutputs()", script)
        self.assertNotIn(".fluidInputs(", script)
        self.assertNotIn(".fluidOutputs(", script)

    def test_generates_gt_recipe_with_output_chances(self):
        draft = RecipeDraft(
            kind="machine",
            template_id="assembler_like",
            item_inputs=[self.item("<minecraft:iron_ore>")],
            item_outputs=[self.item("<minecraft:iron_ingot>"), self.item("<minecraft:gold_nugget>")],
            output_chances=[10000, 2500],
            duration=200,
            eut=30,
        )
        script = self.generator.generate(draft)

        self.assertIn(".itemOutputs([<minecraft:iron_ingot>, <minecraft:gold_nugget>])", script)
        self.assertIn(".outputChances([10000, 2500])", script)

    def test_generates_gt_recipe_with_special_value(self):
        draft = RecipeDraft(
            kind="machine",
            template_id="assembler_like",
            item_inputs=[self.item("<minecraft:iron_ingot>")],
            item_outputs=[self.item("<minecraft:bucket>")],
            special_value=42,
            duration=200,
            eut=30,
        )
        script = self.generator.generate(draft)

        self.assertIn(".specialValue(42)", script)

    def test_generates_gt_recipe_with_special_item(self):
        draft = RecipeDraft(
            kind="machine",
            template_id="assembler_like",
            item_inputs=[self.item("<minecraft:iron_ingot>")],
            item_outputs=[self.item("<minecraft:bucket>")],
            special_item=self.item("<gregtech:gt.integrated_circuit:24>", 0),
            duration=200,
            eut=30,
        )
        script = self.generator.generate(draft)

        self.assertIn(".specialItem(<gregtech:gt.integrated_circuit:24> * 0)", script)

    def test_generates_gt_recipe_remover(self):
        draft = RecipeDraft(
            kind="machine_remove",
            template_id="assembler_like",
            item_inputs=[self.item("<minecraft:piston>"), self.item("<minecraft:slime_ball>")],
            fluid_inputs=[],
        )
        self.assertEqual(
            'mods.gregtech.RecipeRemover.remove("gt.recipe.assembler", [<minecraft:piston>, <minecraft:slime_ball>], []);',
            self.generator.generate(draft).strip(),
        )

    def test_generates_gt_remove_mode_with_multiple_fluid_inputs(self):
        draft = RecipeDraft(
            kind="remove",
            remove_mode="machine",
            template_id="assembler_like",
            item_inputs=[self.item("<minecraft:piston>"), self.item("<ore:stickWood>")],
            fluid_inputs=[ScriptFluid("<liquid:water>", 1000), ScriptFluid("chlorine", 144)],
        )

        self.assertEqual(
            'mods.gregtech.RecipeRemover.remove("gt.recipe.assembler", [<minecraft:piston>, <ore:stickWood>], [<liquid:water> * 1000, <liquid:chlorine> * 144]);',
            self.generator.generate(draft).strip(),
        )

    def test_recipe_maps_include_wiki_values(self):
        self.assertIn("gt.recipe.assembler", RECIPE_MAPS)
        self.assertIn("gt.recipe.largechemicalreactor", RECIPE_MAPS)
        self.assertIn("gtpp.recipe.componentassembler", RECIPE_MAPS)
        self.assertIn("gg.recipe.precise_assembler", RECIPE_MAPS)

    def test_machine_template_options_are_simplified_to_generation_modes(self):
        self.assertEqual(
            [
                "GT RA2",
                "Thermal Expansion Furnace",
                "Thermal Expansion Pulverizer",
                "AE Grinder",
                "AE Inscriber",
            ],
            template_label_options(),
        )
        self.assertEqual("GT RA2", template_label("generic_gt_machine"))
        self.assertEqual("generic_gt_machine", template_id_from_label("GT RA2"))

    def test_legacy_gt_like_template_ids_still_generate_with_old_default_recipe_map(self):
        draft = RecipeDraft(
            kind="machine",
            template_id="cutter_like",
            item_inputs=[self.item("<minecraft:iron_ingot>")],
            item_outputs=[self.item("<minecraft:bucket>")],
            duration=200,
            eut=30,
        )
        script = self.generator.generate(draft)
        self.assertIn("mods.gregtech.RA2", script)
        self.assertIn('.addTo("gt.recipe.cuttingsaw");', script)

    def test_selected_recipe_map_overrides_template_default(self):
        draft = RecipeDraft(
            kind="machine",
            template_id="assembler_like",
            recipe_map="gt.recipe.largechemicalreactor",
            item_inputs=[self.item("<minecraft:iron_ingot>")],
            item_outputs=[self.item("<minecraft:bucket>")],
            duration=200,
            eut=30,
        )
        script = self.generator.generate(draft)
        self.assertIn('.addTo("gt.recipe.largechemicalreactor");', script)

    def test_recipe_map_labels_show_chinese_and_original_id(self):
        label = recipe_map_label("gt.recipe.assembler")
        self.assertEqual("组装机 (gt.recipe.assembler)", label)
        self.assertEqual("gt.recipe.assembler", recipe_map_id_from_label(label))
        self.assertIn("大型化学反应釜 (gt.recipe.largechemicalreactor)", recipe_map_label_options())

    def test_recipe_map_labels_follow_gregtech_lang_names(self):
        self.assertEqual("两极磁化机", recipe_map_label("gt.recipe.polarizer").split(" (", 1)[0])
        self.assertEqual("流体固化器", recipe_map_label("gt.recipe.fluidsolidifier").split(" (", 1)[0])
        self.assertEqual("板材切割机", recipe_map_label("gt.recipe.cuttingsaw").split(" (", 1)[0])
        self.assertEqual("石油裂化机", recipe_map_label("gt.recipe.craker").split(" (", 1)[0])
        self.assertEqual("鸿蒙之眼", recipe_map_label("gt.recipe.eyeofharmony").split(" (", 1)[0])
        self.assertEqual("电动聚爆压缩机", recipe_map_label("gt.recipe.electricimplosioncompressor").split(" (", 1)[0])


if __name__ == "__main__":
    unittest.main()
