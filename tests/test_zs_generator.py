import unittest

from core.recipe_model import RecipeDraft, ScriptFluid, ScriptItem
from core.zs_generator import ZsGenerator


class ZsGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.generator = ZsGenerator()

    def item(self, expression, amount=1):
        return ScriptItem(expression=expression, amount=amount, comment_name="")

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
            template_id="generic_gt_machine",
            item_inputs=[self.item("<minecraft:iron_ingot>")],
            item_outputs=[self.item("<minecraft:bucket>")],
            fluid_inputs=[ScriptFluid("water", 1000)],
            fluid_outputs=[],
            duration=200,
            eut=30,
        )
        script = self.generator.generate(draft)
        self.assertIn("mods.gregtech.GenericMachine.addRecipe", script)
        self.assertIn("<liquid:water> * 1000", script)
        self.assertIn("200", script)
        self.assertIn("30", script)


if __name__ == "__main__":
    unittest.main()
