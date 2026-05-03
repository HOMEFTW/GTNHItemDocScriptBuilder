# ToDOLIST

## 下一步优先事项

- [ ] Keep the current GUI three-pane ratio as the first UI priority: left search `580px`, right preview `400px`, center editor gets the remaining space.
- [ ] Add RA2 optional fields from the wiki and real scripts: `.noOptimize()`.

## 来自 `D:\Code\ZZZ-NxerCustoms.zs` 的记录

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

## 已完成

- [x] 增加应用基本信息和“关于”对话框：右上角“关于”按钮显示 `GTNHItemDocScriptBuilder`、版本 `1.0.0`、工作室 `Andgatech`。
- [x] 手写模式下切换脚本类型自动清空配方格和流体行，避免旧类型内容误带入新类型。
- [x] 使用项目目录下的 `icon.ico` 作为 Tk 窗口图标和 PyInstaller exe 图标，并作为运行时资源打包。
- [x] 加高主窗口：默认高度改为 `1080`，最小高度改为 `1040`；上方两个列表高度不变，新增高度留给下面三栏。
- [x] 增加脚本草稿列表：可保存当前草稿、载入选中草稿、删除选中草稿，并按列表顺序把全部草稿追加到完整脚本。
- [x] 增加生成前草稿校验：`添加到脚本` 和 `替换原配方` 会阻止无效草稿写入完整脚本，并提示缺输入/输出或数字字段非法。
- [x] 增加未导入 `.zs` 时的新建/保存工作流：`新建 .zs` 创建并绑定当前脚本文件，`保存` 直接覆盖当前文件，`另存为` 切换当前文件路径，并在工具栏显示当前路径。
- [x] 将机器“模板”简化为“生成方式”：GT 只保留 `GT RA2`，具体机器改由 `Recipe Map` 选择；旧 GT-like 模板 ID 自动迁移并保留默认 recipe map。
- [x] 增加解析模式：点击“解析到GUI”后切换脚本类型会自动按当前类型重新解析，点击“关闭解析”后回到手动草稿模式。
- [x] 增加脚本编辑安全能力：“添加到脚本”可选择文件末尾、当前光标、当前配方后，并支持“替换原配方”。
- [x] 增强配方列表摘要：合成显示 `输出 <- 输入`，GT 显示 `recipe map: 输入 -> 输出`，删除显示删除目标。
- [x] 当前草稿自动生成中文注释，合成和 GT 机器会根据物品、流体、数量和 recipe map 写说明。
- [x] 自动注释中有中文名的物品/流体显示为 `中文名 <ct表达式> * 数量`。
- [x] 增加当前脚本类型的配方列表：显示序号、行号、类型和摘要，点击某行可直接解析到 GUI。
- [x] 增加 `.zs` 解析导航按钮：第一条、上一条、下一条、最后一条，可在当前脚本类型的匹配配方之间切换。
- [x] 将 GT 机器流体输入和流体输出改成分别可填写条数的动态 UI，默认各 1 条。
- [x] 压缩顶部工具栏按钮宽度和间距，减少按钮挤占界面空间。
- [x] 修复顶部工具栏按钮过紧导致文字难以辨认的问题，中文按钮按显示宽度预留空间。
- [x] 将顶部工具栏改成两排按钮，并把“选索引”恢复为“选择 item_index.json”。
- [x] 将默认窗口高度增加到 `980`，最小高度和旧配置归一化高度增加到 `960`。
- [x] 给中间编辑栏增加竖向滚动条，参数和格子过多时可向下滚动查看。
- [x] 完善 GT `RecipeRemover.remove(...)` 编辑器：物品输入使用 16 格，流体输入使用独立 4 行列表并支持搜索和数量。
- [x] 增加 `.zs` 导入继续编辑 MVP：可解析本工具生成的 RA2、GT 删除、合成、熔炉和燃料脚本并填回当前 GUI 草稿。
- [x] 修复导入和切换脚本类型后的 ZS 预览语义：预览只代表当前一份草稿，导入按脚本顺序解析第一条受支持配方。
- [x] 将右侧 ZS 预览分成上下两半：完整 `.zs` 文件原文和当前草稿保存内容，并显示当前草稿来源行号。
- [x] 重做 `.zs` 编辑工作流：导入默认不解析，解析按钮按当前脚本类型回填 GUI，添加到脚本后保存完整文件，并支持撤销/重做。
- [x] 将 GTNH/模组机器输出格从 4 格调整为 9 格，匹配 GT 输出 UI。
- [x] 增加 RA2 `.specialItem(...)` 支持，可从当前选中的物品格复制物品、数量和后缀。
- [x] 增加 RA2 `.specialValue(...)` 支持，GT 机器参数区可填写整数 special value。
- [x] 增加 RA2 `.outputChances(...)` 输出概率支持，GT 机器输出格可按 `10000 = 100%` 编辑概率。
- [x] 修复参数和流体区的脚本类型显隐：有序/无序不显示流体，机器和 GT 删除才显示对应流体能力。
- [x] 让 MineTweaker 专项参数按脚本类型显示：镜像只在有序、XP 只在熔炉、燃烧时间只在燃料。
- [x] 将 MineTweaker 参数区的新控件左对齐，避免“写入熔炉 XP”等选项离左边太远。
- [x] 增加 MineTweaker GUI 和生成器支持：镜像有序合成、可选熔炉 XP、熔炉燃料脚本。
- [x] Add `fluid_index.json` export in `GTNHItemDocExporter` from Forge `FluidRegistry`.
- [x] Load `fluid_index.json` in the GUI and make fluid input/output rows searchable like items.
- [x] Split recipe slot UI by script type: shaped/shapeless `3 x 3 + 1`, furnace `1 + 1`, machine `16 + 4`.
- [x] Add delete-mode sub options for shaped, shapeless, furnace, and GT layouts.
- [x] Widen the center editor pane and compact slot buttons so recipe controls remain visible.
- [x] Add a horizontal scrollbar to the left item search results table.
- [x] Increase the default window width and make the center editor pane the primary layout area.
- [x] Rework fluid rows so the amount field stays visible without making the whole window too wide.
- [x] Rename the remove sub-option label to "删除布局" and verify its layout selector is visible.
- [x] Keep left search and right preview panes fixed-width so the center editor keeps the usable space.
- [x] Shift about one third of the center editor width back to the left search pane.
- [x] Add vertical and horizontal scrollbars to the ZS preview panel.
- [x] Prevent the preview scrollbars from expanding the preview pane and squeezing the editor.
- [x] Support ore dictionary expressions such as `<ore:stickWood>` and `<ore:dustClay>` as first-class selectable inputs.
- [x] Support item expressions with amount `*0`, used by GT molds and integrated circuits in RA2 recipes.
- [x] Support output/input NBT expressions such as `.withTag({baseCapacity: 4611686018427385856 as long})`.
- [x] Increase GUI window height so newly added editor controls are visible.
- [x] Add RA2 toggles for `.noFluidInputs()` and `.noFluidOutputs()`.
