"""Generate CraftTweaker and ModTweaker ZS scripts."""
from typing import Iterable, Optional

from core.recipe_model import RecipeDraft, ScriptFluid, ScriptItem
from core.templates import TEMPLATES


class ZsGenerator:
    def generate(self, draft: RecipeDraft) -> str:
        if draft.kind == "shaped":
            return self._shaped(draft)
        if draft.kind == "shapeless":
            return self._shapeless(draft)
        if draft.kind == "furnace":
            return self._furnace(draft)
        if draft.kind == "remove":
            return self._remove(draft)
        if draft.kind == "machine":
            return self._machine(draft)
        if draft.kind == "machine_remove":
            return self._machine_remove(draft)
        raise ValueError(f"Unknown recipe kind: {draft.kind}")

    def _shaped(self, draft: RecipeDraft) -> str:
        output = self._first_required_item(draft.item_outputs, "Shaped recipe needs an output")
        inputs = self._padded_items(draft.item_inputs, 9)
        rows = [self._item_array(inputs[index : index + 3]) for index in range(0, 9, 3)]
        return "recipes.addShaped({}, [\n    {},\n    {},\n    {}\n]);".format(output.to_zs(), *rows)

    def _shapeless(self, draft: RecipeDraft) -> str:
        output = self._first_required_item(draft.item_outputs, "Shapeless recipe needs an output")
        inputs = self._present_items(draft.item_inputs)
        if not inputs:
            raise ValueError("Shapeless recipe needs at least one input")
        return f"recipes.addShapeless({output.to_zs()}, {self._item_array(inputs)});"

    def _furnace(self, draft: RecipeDraft) -> str:
        output = self._first_required_item(draft.item_outputs, "Furnace recipe needs an output")
        input_item = self._first_required_item(draft.item_inputs, "Furnace recipe needs an input")
        return f"furnace.addRecipe({output.to_zs()}, {input_item.to_zs()}, {float(draft.xp):.1f});"

    def _remove(self, draft: RecipeDraft) -> str:
        if draft.remove_mode == "machine":
            return self._machine_remove(draft)
        output = self._first_required_item(draft.item_outputs, "Recipe removal needs a target output")
        if draft.remove_mode == "shaped":
            return f"recipes.removeShaped({output.to_zs()});"
        if draft.remove_mode == "shapeless":
            return f"recipes.removeShapeless({output.to_zs()});"
        if draft.remove_mode == "furnace":
            inputs = self._present_items(draft.item_inputs)
            if inputs:
                return f"furnace.remove({output.to_zs()}, {inputs[0].to_zs()});"
            return f"furnace.remove({output.to_zs()});"
        return f"recipes.remove({output.to_zs()});"

    def _machine(self, draft: RecipeDraft) -> str:
        template = TEMPLATES.get(draft.template_id)
        if template is None:
            raise ValueError(f"Unknown machine template: {draft.template_id}")
        if template.style == "te_furnace":
            input_item = self._first_required_item(draft.item_inputs, "Thermal Expansion furnace needs an input")
            output = self._first_required_item(draft.item_outputs, "Thermal Expansion furnace needs an output")
            return f"mods.thermalexpansion.Furnace.addRecipe({draft.eut}, {input_item.to_zs()}, {output.to_zs()});"
        if template.style == "te_pulverizer":
            return self._te_pulverizer(draft)
        if template.style == "ae_grinder":
            return self._ae_grinder(draft)
        if template.style == "ae_inscriber":
            return self._ae_inscriber(draft)
        return self._generic_gt(draft)

    def _te_pulverizer(self, draft: RecipeDraft) -> str:
        input_item = self._first_required_item(draft.item_inputs, "Thermal Expansion pulverizer needs an input")
        outputs = self._present_items(draft.item_outputs)
        if not outputs:
            raise ValueError("Thermal Expansion pulverizer needs an output")
        secondary = outputs[1].to_zs() if len(outputs) > 1 else "null"
        chance = 100 if len(outputs) > 1 else 0
        return (
            "mods.thermalexpansion.Pulverizer.addRecipe("
            f"{draft.eut}, {input_item.to_zs()}, {outputs[0].to_zs()}, {secondary}, {chance});"
        )

    def _ae_grinder(self, draft: RecipeDraft) -> str:
        input_item = self._first_required_item(draft.item_inputs, "AE grinder needs an input")
        outputs = self._present_items(draft.item_outputs)
        if not outputs:
            raise ValueError("AE grinder needs an output")
        optional1 = outputs[1].to_zs() if len(outputs) > 1 else "null"
        optional2 = outputs[2].to_zs() if len(outputs) > 2 else "null"
        chance1 = 100 if len(outputs) > 1 else 0
        chance2 = 100 if len(outputs) > 2 else 0
        return (
            "mods.appeng.Grinder.addRecipe("
            f"{input_item.to_zs()}, {outputs[0].to_zs()}, {draft.eut}, {optional1}, {chance1}, {optional2}, {chance2});"
        )

    def _ae_inscriber(self, draft: RecipeDraft) -> str:
        inputs = self._padded_items(draft.item_inputs, 3)
        output = self._first_required_item(draft.item_outputs, "AE inscriber needs an output")
        center = self._item_or_null(inputs[0])
        top = self._item_or_null(inputs[1])
        bottom = self._item_or_null(inputs[2])
        return f"mods.appeng.Inscriber.addRecipe({center}, {top}, {bottom}, {output.to_zs()}, \"Inscriber\");"

    def _generic_gt(self, draft: RecipeDraft) -> str:
        template = TEMPLATES[draft.template_id]
        outputs = self._present_items(draft.item_outputs)
        if not outputs:
            raise ValueError("GTNH machine template needs at least one item output")
        recipe_map = self._recipe_map(draft, template)
        return (
            f"// GTNH RA2 recipe map: {recipe_map}\n"
            "mods.gregtech.RA2\n"
            "    .builder()\n"
            f"    .itemInputs({self._item_array(self._present_items(draft.item_inputs))})\n"
            f"    .itemOutputs({self._item_array(outputs)})\n"
            f"    .fluidInputs({self._fluid_array(draft.fluid_inputs)})\n"
            f"    .fluidOutputs({self._fluid_array(draft.fluid_outputs)})\n"
            f"    .duration({draft.duration})\n"
            f"    .eut({draft.eut})\n"
            f"    .addTo(\"{recipe_map}\");"
        )

    def _machine_remove(self, draft: RecipeDraft) -> str:
        template = TEMPLATES.get(draft.template_id)
        if template is None:
            raise ValueError(f"Unknown machine template: {draft.template_id}")
        if template.style != "generic_gt":
            raise ValueError("Machine recipe remover is only available for GT recipe map templates")
        inputs = self._present_items(draft.item_inputs)
        if not inputs and not draft.fluid_inputs:
            raise ValueError("GT recipe remover needs at least one item or fluid input")
        recipe_map = self._recipe_map(draft, template)
        return (
            "mods.gregtech.RecipeRemover.remove("
            f"\"{recipe_map}\", {self._item_array(inputs)}, {self._fluid_array(draft.fluid_inputs)});"
        )

    def _recipe_map(self, draft: RecipeDraft, template) -> str:
        return draft.recipe_map.strip() or template.recipe_map or "gt.recipe.assembler"

    def _first_required_item(self, items: Iterable[Optional[ScriptItem]], message: str) -> ScriptItem:
        for item in items:
            if item is not None:
                return item
        raise ValueError(message)

    def _present_items(self, items: Iterable[Optional[ScriptItem]]) -> list[ScriptItem]:
        return [item for item in items if item is not None]

    def _padded_items(self, items: Iterable[Optional[ScriptItem]], count: int) -> list[Optional[ScriptItem]]:
        result = list(items)[:count]
        while len(result) < count:
            result.append(None)
        return result

    def _item_or_null(self, item: Optional[ScriptItem]) -> str:
        return "null" if item is None else item.to_zs()

    def _item_array(self, items: Iterable[Optional[ScriptItem]]) -> str:
        return "[" + ", ".join(self._item_or_null(item) for item in items) + "]"

    def _fluid_array(self, fluids: Iterable[ScriptFluid]) -> str:
        return "[" + ", ".join(fluid.to_zs() for fluid in fluids) + "]"
