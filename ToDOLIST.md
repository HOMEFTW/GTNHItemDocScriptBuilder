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

## 中文开发启示

- `item_index.json` 只能解决物品/方块选择，不能完整解决流体选择；下一步需要 exporter 从 `FluidRegistry` 导出 `fluid_index.json`。
- 流体名不能靠简单英文单词假设，真实脚本里存在 `molten.siliconsolargrade`、`acid naquadah emulsion`、`liquid helium` 这种带点号或空格的注册名。
- GUI 的流体输入/输出不应继续只是手输框，应改成和物品一样的搜索表、双击填入、数量输入。
- GTNH 脚本常用 ore dictionary 作为输入，GUI 需要单独的 `<ore:...>` 输入能力；它不是物品索引里的普通物品。
- RA2 配方里 `*0` 是有效语义，常用于编程电路和模具；数量控件不能强制最小值为 1。
- `.withTag(...)` 是实际脚本中会用到的核心能力，尤其是 ME 仓、工具部件或带 NBT 的机器；脚本模型需要给物品表达式保留原始后缀。
- RA2 builder 需要支持“无流体输入/输出”的显式链式调用，即 `.noFluidInputs()` 和 `.noFluidOutputs()`，不能只用空数组代替。
- `RecipeRemover.remove` 需要独立编辑器：目标 recipe map、物品输入数组、流体输入数组都要能为空或多项。
- `furnace.addRecipe` 在真实脚本里有两参数写法；GUI 可以保留 XP 字段，但生成器需要支持“不写 XP”的选项。
- 现有 GUI 的 recipe map 选择是正确方向，因为真实脚本在 assembler、extruder、electrolyzer、largechemicalreactor、distillationtower、brewer、multielectro 等多张 map 间切换非常频繁。
- 完整 `.zs` 导入功能值得做：先不追求编辑所有语法，至少可以解析 RA2 块、CraftTweaker 合成、furnace、RecipeRemover，生成可继续编辑的草稿。
