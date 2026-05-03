import unittest

from core.recipe_model import RecipeDraft, ScriptFluid, ScriptItem
from core.zs_generator import ZsGenerator
from core.zs_parser import parse_zs_script, parse_zs_script_matches, parse_zs_script_with_source


class ZsParserTest(unittest.TestCase):
    def setUp(self):
        self.generator = ZsGenerator()

    def item(self, expression, amount=1, suffix=""):
        return ScriptItem(expression=expression, amount=amount, suffix=suffix)

    def test_parses_generated_gt_machine_recipe_for_reediting(self):
        draft = RecipeDraft(
            kind="machine",
            recipe_map="gt.recipe.largechemicalreactor",
            item_inputs=[self.item("<gregtech:gt.integrated_circuit:21>", 0)],
            item_outputs=[self.item("<minecraft:bucket>"), self.item("<minecraft:gold_nugget>")],
            output_chances=[10000, 2500],
            fluid_inputs=[ScriptFluid("water", 1000)],
            fluid_outputs=[],
            special_value=42,
            duration=320,
            eut=120,
        )

        parsed = parse_zs_script(self.generator.generate(draft))

        self.assertEqual("machine", parsed.kind)
        self.assertEqual("gt.recipe.largechemicalreactor", parsed.recipe_map)
        self.assertEqual("<gregtech:gt.integrated_circuit:21>", parsed.item_inputs[0].expression)
        self.assertEqual(0, parsed.item_inputs[0].amount)
        self.assertEqual("<minecraft:gold_nugget>", parsed.item_outputs[1].expression)
        self.assertEqual([10000, 2500], parsed.output_chances)
        self.assertEqual("<liquid:water> * 1000", parsed.fluid_inputs[0].to_zs())
        self.assertEqual(42, parsed.special_value)
        self.assertEqual(320, parsed.duration)
        self.assertEqual(120, parsed.eut)

    def test_parses_first_supported_recipe_by_script_order(self):
        script = (
            "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);\n"
            'mods.gregtech.RecipeRemover.remove("gt.recipe.assembler", [<minecraft:piston>], []);'
        )

        parsed = parse_zs_script(script)

        self.assertEqual("shapeless", parsed.kind)
        self.assertEqual("<minecraft:stick>", parsed.item_outputs[0].expression)

    def test_reports_imported_recipe_source_line(self):
        script = (
            "// header\n"
            "\n"
            "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);\n"
            'mods.gregtech.RecipeRemover.remove("gt.recipe.assembler", [<minecraft:piston>], []);'
        )

        parsed = parse_zs_script_with_source(script)

        self.assertEqual("shapeless", parsed.draft.kind)
        self.assertEqual(1, parsed.recipe_number)
        self.assertEqual(3, parsed.line_number)
        self.assertEqual("recipes.addShapeless", parsed.marker)

    def test_source_recipe_number_counts_repeated_supported_calls(self):
        script = (
            "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);\n"
            "recipes.addShapeless(<minecraft:torch> * 4, [<minecraft:coal>, <minecraft:stick>]);\n"
        )

        parsed = parse_zs_script_with_source(script)

        self.assertEqual(1, parsed.recipe_number)
        self.assertEqual(1, parsed.line_number)

    def test_parses_requested_occurrence_for_current_kind(self):
        script = (
            "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);\n"
            "recipes.addShapeless(<minecraft:torch> * 4, [<minecraft:coal>, <minecraft:stick>]);\n"
            "recipes.addShapeless(<minecraft:chest>, [<minecraft:planks>]);\n"
        )

        parsed = parse_zs_script_with_source(script, allowed_kinds={"shapeless"}, occurrence=1)

        self.assertEqual("<minecraft:torch>", parsed.draft.item_outputs[0].expression)
        self.assertEqual(2, parsed.recipe_number)
        self.assertEqual(2, parsed.line_number)
        self.assertEqual(2, parsed.parseable_index)
        self.assertEqual(3, parsed.parseable_count)

    def test_negative_occurrence_parses_last_current_kind(self):
        script = (
            "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);\n"
            "recipes.addShapeless(<minecraft:torch> * 4, [<minecraft:coal>, <minecraft:stick>]);\n"
        )

        parsed = parse_zs_script_with_source(script, allowed_kinds={"shapeless"}, occurrence=-1)

        self.assertEqual("<minecraft:torch>", parsed.draft.item_outputs[0].expression)
        self.assertEqual(2, parsed.parseable_index)
        self.assertEqual(2, parsed.parseable_count)

    def test_lists_all_matches_for_current_kind(self):
        script = (
            "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);\n"
            "mods.gregtech.RA2.builder().itemInputs([<minecraft:piston>]).itemOutputs([<minecraft:bucket>])"
            ".fluidInputs([]).fluidOutputs([]).duration(200).eut(30).addTo(\"gt.recipe.assembler\");\n"
            "recipes.addShapeless(<minecraft:torch> * 4, [<minecraft:coal>, <minecraft:stick>]);\n"
        )

        matches = parse_zs_script_matches(script, allowed_kinds={"shapeless"})

        self.assertEqual(2, len(matches))
        self.assertEqual("<minecraft:stick>", matches[0].draft.item_outputs[0].expression)
        self.assertEqual("<minecraft:torch>", matches[1].draft.item_outputs[0].expression)
        self.assertEqual(1, matches[0].parseable_index)
        self.assertEqual(2, matches[1].parseable_index)
        self.assertEqual(3, matches[1].recipe_number)
        self.assertEqual(3, matches[1].line_number)

    def test_reports_source_offsets_for_replacement(self):
        script = (
            "// header\n"
            "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);\n"
            "recipes.addShapeless(<minecraft:torch> * 4, [<minecraft:coal>, <minecraft:stick>]);\n"
            "// footer"
        )

        parsed = parse_zs_script_with_source(script, allowed_kinds={"shapeless"}, occurrence=1)

        self.assertEqual(
            "recipes.addShapeless(<minecraft:torch> * 4, [<minecraft:coal>, <minecraft:stick>]);",
            script[parsed.start_offset : parsed.end_offset],
        )

    def test_reports_gt_machine_source_offsets_through_add_to(self):
        script = (
            "// before\n"
            "mods.gregtech.RA2\n"
            "    .builder()\n"
            "    .itemInputs([<minecraft:piston>])\n"
            "    .itemOutputs([<minecraft:bucket>])\n"
            "    .fluidInputs([])\n"
            "    .fluidOutputs([])\n"
            "    .duration(200)\n"
            "    .eut(30)\n"
            "    .addTo(\"gt.recipe.assembler\");\n"
            "// after"
        )

        parsed = parse_zs_script_with_source(script, allowed_kinds={"machine"})

        self.assertTrue(script[parsed.start_offset : parsed.end_offset].startswith("mods.gregtech.RA2"))
        self.assertTrue(script[parsed.start_offset : parsed.end_offset].endswith('.addTo("gt.recipe.assembler");'))
        self.assertNotIn("// after", script[parsed.start_offset : parsed.end_offset])

    def test_parses_only_requested_script_kind(self):
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

        parsed = parse_zs_script_with_source(script, allowed_kinds={"machine"})

        self.assertEqual("machine", parsed.draft.kind)
        self.assertEqual(2, parsed.recipe_number)
        self.assertEqual(2, parsed.line_number)

    def test_parses_gt_recipe_remover_for_reediting_after_restart(self):
        script = (
            'mods.gregtech.RecipeRemover.remove("gt.recipe.assembler", '
            "[<minecraft:piston>, <ore:stickWood>*0], "
            "[<liquid:water> * 1000, <liquid:chlorine> * 144]);"
        )

        parsed = parse_zs_script(script)

        self.assertEqual("remove", parsed.kind)
        self.assertEqual("machine", parsed.remove_mode)
        self.assertEqual("gt.recipe.assembler", parsed.recipe_map)
        self.assertEqual("<minecraft:piston>", parsed.item_inputs[0].expression)
        self.assertEqual("<ore:stickWood>", parsed.item_inputs[1].expression)
        self.assertEqual(0, parsed.item_inputs[1].amount)
        self.assertEqual("<liquid:water> * 1000", parsed.fluid_inputs[0].to_zs())
        self.assertEqual("<liquid:chlorine> * 144", parsed.fluid_inputs[1].to_zs())

    def test_parses_generated_minetweaker_recipes(self):
        shaped = parse_zs_script(
            "recipes.addShapedMirrored(<minecraft:chest>, [\n"
            "    [<minecraft:planks>, <minecraft:planks>, <minecraft:planks>],\n"
            "    [<minecraft:planks>, null, <minecraft:planks>],\n"
            "    [<minecraft:planks>, <minecraft:planks>, <minecraft:planks>]\n"
            "]);"
        )
        shapeless = parse_zs_script("recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);")
        furnace = parse_zs_script("furnace.addRecipe(<minecraft:glass>, <minecraft:sand>, 0.5);")
        fuel = parse_zs_script("furnace.setFuel(<minecraft:coal>, 1600);")

        self.assertEqual("shaped", shaped.kind)
        self.assertTrue(shaped.shaped_mirrored)
        self.assertEqual(9, len(shaped.item_inputs))
        self.assertIsNone(shaped.item_inputs[4])
        self.assertEqual("shapeless", shapeless.kind)
        self.assertEqual(4, shapeless.item_outputs[0].amount)
        self.assertEqual("furnace", furnace.kind)
        self.assertEqual(0.5, furnace.xp)
        self.assertEqual("fuel", fuel.kind)
        self.assertEqual(1600, fuel.fuel_ticks)


if __name__ == "__main__":
    unittest.main()
