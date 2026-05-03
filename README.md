# GTNHItemDocScriptBuilder

Tkinter 桌面工具，用 `GTNHItemDocExporter` 导出的 `item_index.json` 生成 CraftTweaker / ModTweaker `.zs` 脚本。

## 运行

```powershell
python main.py
```

## 输入

选择导出的物品索引，例如：

```text
D:\Code\gtnh_item_doc_exporter\item_index.json
```

如果同目录存在 `fluid_index.json`，GUI 会自动加载流体索引。GTNH/模组机器模板中的“流体输入”和“流体输出”可以点击“搜索”，按中文名、`fluidName` 或 `<liquid:...>` 表达式查找流体，双击后填入当前流体行。

如果同目录存在 `ore_dictionary_index.json`，GUI 会自动加载矿物字典索引。先点击一个配方输入格，再点击工具栏的“填入 OreDict”，可以按 `oreName`、`<ore:...>` 表达式或包含的物品表达式搜索，双击后会把 `<ore:...>` 写入当前输入格。OreDict 只作为输入使用，不会填入输出格。

## 支持脚本

- 有序合成
- 镜像有序合成 `recipes.addShapedMirrored`
- 无序合成
- 熔炉配方
- 熔炉燃料 `furnace.setFuel`
- 删除配方
- GTNH / 模组机器模板配方
- 矿物字典输入 `<ore:...>`
- 物品数量 `*0` 和 `.withTag(...)` 后缀
- RA2 `.outputChances(...)` 输出概率
- RA2 `.specialValue(...)`
- RA2 `.noFluidInputs()` / `.noFluidOutputs()` 开关

不同脚本类型使用独立配方格界面：有序合成和无序合成为 `3 x 3` 输入加 1 个输出，熔炉为 1 个输入加 1 个输出，燃料为 1 个输入且无输出，GTNH/模组机器为 16 个物品输入加 4 个物品输出。机器模板支持流体输入/输出、`duration` 和 `EU/t`。其中 Thermal Expansion 与 AE 模板参考 ModTweaker 的 logger 输出；GT 机器模板参考 Minetweaker-Gregtech-5-Addon Wiki 的 RA2 builder 语法：

点击任意物品格后，中间的“选中物品格”区域可以编辑数量和后缀。数量允许 `0`，用于 GT 编程电路或模具这类 `<...> * 0` 输入；后缀会直接拼接到物品表达式之后，可填写 `.withTag(...)` 这类 NBT 表达式。GTNH/模组机器模式下选中输出格时，还可以填写“输出概率”，单位为 GT 常用的 `10000 = 100%`，会生成 RA2 的 `.outputChances([...])`。

删除模式下会显示“删除类型”子选项，可选择有序、无序、熔炉或 GT，并切换到对应的独立配方格界面。

参数区提供 MineTweaker 常用选项：“镜像有序合成”会让有序合成生成 `recipes.addShapedMirrored(...)`；“写入熔炉 XP”关闭后，熔炉配方会生成两参数写法 `furnace.addRecipe(output, input);`；“燃烧时间”用于燃料模式生成 `furnace.setFuel(item, ticks);`。

参数和流体区会按脚本类型显示：有序/无序合成不显示流体，熔炉只显示 XP，燃料只显示燃烧时间，GTNH/模组机器显示模板、`Recipe Map`、`Duration`、`EU/t`、无流体开关和流体输入/输出。删除模式只有选择 `GT` 时才显示 `Recipe Map` 和流体输入。

GTNH/模组机器参数区的 `Special Value` 默认留空，不生成脚本；填入整数后会生成 `.specialValue(value)`。

GUI 的第一 UI 优先级是保持当前三栏比例：左侧物品搜索栏固定宽度，右侧 ZS 预览固定宽度，中间编辑区使用剩余空间。默认窗口为 `1500 x 920`，旧保存配置的高度低于 `900` 时会自动提升；后续新增控件时必须先保证这个比例不被破坏；左侧和右侧长内容依靠各自滚动条查看，不允许撑宽侧栏挤压中间编辑区。

GTNH/模组机器模式下，“模板”下方有 `Recipe Map` 下拉框。列表来自 Wiki 的 `Available recipe maps`，界面会显示中文名和原 ID，例如 `组装机 (gt.recipe.assembler)`；选择后会覆盖模板默认 recipe map，生成脚本时仍使用括号中的原 ID。参数区的“无流体输入”和“无流体输出”会生成 RA2 的 `.noFluidInputs()` / `.noFluidOutputs()`，并跳过对应的 `.fluidInputs(...)` / `.fluidOutputs(...)`。

```zenscript
mods.gregtech.RA2
    .builder()
    .itemInputs([<minecraft:dirt>])
    .itemOutputs([<minecraft:obsidian>])
    .duration(420)
    .eut(100)
    .addTo("gt.recipe.assembler");
```

删除 GT 机器配方时可在“删除模式”选择 `machine`，会生成：

```zenscript
mods.gregtech.RecipeRemover.remove("gt.recipe.assembler", [<minecraft:piston>, <minecraft:slime_ball>], []);
```

## 打包

```powershell
.\build.bat
```
