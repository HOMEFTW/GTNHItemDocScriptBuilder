# ToDOLIST

## Next Priorities

- [ ] Add `fluid_index.json` export in `GTNHItemDocExporter` from Forge `FluidRegistry`.
- [ ] Load `fluid_index.json` in the GUI and make fluid input/output rows searchable like items.
- [ ] Support ore dictionary expressions such as `<ore:stickWood>` and `<ore:dustClay>` as first-class selectable inputs.
- [ ] Support item expressions with amount `*0`, used by GT molds and integrated circuits in RA2 recipes.
- [ ] Support output/input NBT expressions such as `.withTag({baseCapacity: 4611686018427385856 as long})`.
- [ ] Add RA2 toggles for `.noFluidInputs()` and `.noFluidOutputs()`.
- [ ] Add RA2 optional fields from the wiki and real scripts: `.outputChances(...)`, `.noOptimize()`, `.specialValue(...)`, `.specialItem(...)`.
- [ ] Improve `RecipeRemover.remove` editor for multi-line item/fluid input removal.
- [ ] Add import/parse support for existing `.zs` scripts so complete scripts like `ZZZ-NxerCustoms.zs` can seed GUI drafts.

## Notes From `D:\Code\ZZZ-NxerCustoms.zs`

- Uses CraftTweaker shaped/shapeless recipes with both compact one-line and multi-line formatting.
- Uses furnace recipes with two arguments, while current generator emits three arguments with XP for the explicit furnace mode.
- Uses many ore dictionary ingredients (`<ore:...>`), so the GUI needs an ore dictionary source or manual ore-expression insertion.
- Uses GT RA2 builder extensively with `.itemInputs`, `.itemOutputs`, `.fluidInputs`, `.fluidOutputs`, `.eut`, `.duration`, `.addTo`.
- Uses fluids that cannot be recovered reliably from `item_index.json`, for example `<liquid:molten.siliconsolargrade>`, `<liquid:chlorine>`, `<liquid:dilutedsulfuricacid>`, and names containing spaces such as `<liquid:liquid helium>`.
- Uses `.noFluidOutputs()` and `.noFluidInputs()` in valid RA2 chains.
- Uses `RecipeRemover.remove(recipeMap, itemInputs, fluidInputs)` with empty arrays, one-line calls, and multi-line calls.
- Uses NBT item expressions with `.withTag(...)`.
- Uses GT integrated circuits and molds as zero-count inputs, for example `<gregtech:gt.integrated_circuit:21>*0` and `<gregtech:gt.metaitem.01:32351>*0`.
- Recipe maps observed in this script: `gt.recipe.alloysmelter`, `gt.recipe.assembler`, `gt.recipe.brewer`, `gt.recipe.chemicalreactor`, `gt.recipe.distillationtower`, `gt.recipe.electricimplosioncompressor`, `gt.recipe.electrolyzer`, `gt.recipe.extruder`, `gt.recipe.implosioncompressor`, `gt.recipe.largechemicalreactor`, `gtpp.recipe.multielectro`.
- Fluid expressions observed include `water`, `chlorine`, `oxygen`, `sulfuricacid`, `dilutedsulfuricacid`, `ender`, `sodiumpotassium`, `molten.siliconsolargrade`, `molten.infinity`, `molten.cosmicneutronium`, and fluid names with spaces.
- Ore dictionary expressions observed include `stickWood`, `dustClay`, `ingotIron`, `gemMalachite`, `crystalFluix`, `itemCertusQuartz`, and multiple Orichalcum processing forms.
