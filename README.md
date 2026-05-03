# GTNHItemDocScriptBuilder

`GTNHItemDocScriptBuilder` 是一个 Tkinter 桌面 GUI 工具，用 [`GTNHItemDocExporter`](https://github.com/HOMEFTW/GTNHItemDocExporter) 导出的索引文件生成和维护 CraftTweaker / ModTweaker / GregTech `.zs` 脚本。

- GitHub：<https://github.com/HOMEFTW/GTNHItemDocScriptBuilder>
- 当前版本：`1.0.0`
- 工作室：`Andgatech`
- 配套导出模组：[`GTNHItemDocExporter`](https://github.com/HOMEFTW/GTNHItemDocExporter)

应用信息可通过窗口右上角“关于”按钮查看：`GTNHItemDocScriptBuilder`，版本 `1.0.0`，工作室 `Andgatech`。

## 项目关系

[`GTNHItemDocExporter`](https://github.com/HOMEFTW/GTNHItemDocExporter) 是运行在 GTNH 客户端里的 Forge 模组，负责从真实游戏环境导出 `item_index.json`、`fluid_index.json` 和 `ore_dictionary_index.json`。

本应用读取这些导出文件，提供搜索、配方草稿、脚本预览、导入解析和保存能力，用鼠标操作辅助编写 `.zs` 脚本。

推荐流程：

1. 使用 `GTNHItemDocExporter` 在 GTNH 客户端生成索引文件。
2. 在本应用中选择导出目录里的 `item_index.json`。
3. GUI 会自动尝试加载同目录的 `fluid_index.json` 和 `ore_dictionary_index.json`。
4. 在 GUI 中编写、导入、替换或保存 `.zs` 脚本。

## 运行

```powershell
python main.py
```

## 导入继续编辑

未导入 `.zs` 时可以直接从空白模式开始写：点击“新建 .zs”会先选择并创建一个空脚本文件，右侧上半区绑定为当前文件；之后点击“添加到脚本”把当前草稿加入完整脚本，再点击“保存”会直接覆盖当前文件。未新建也未导入时点击“保存”，会自动走“另存为”。“另存为”会把右侧上半区完整脚本保存到新路径，并把该路径设为当前文件。工具栏会显示当前文件路径。

工具栏的“导入 .zs”只会读取已保存的完整脚本，并放到右侧上半区，不会自动解析或改动当前 GUI 草稿。默认状态适合直接写完整 `.zs` 文件。

需要从脚本回填 GUI 时，先选择左侧“脚本类型”，再点击“解析到GUI”。解析器只会按当前脚本类型查找配方，例如选“有序合成”只解析 `recipes.addShaped...`，选“GTNH/模组机器”只解析 RA2 builder，避免有序合成误解析到 GT 机器里。解析成功后会进入解析模式，此时切换脚本类型或删除子类型会自动按新类型重新解析完整脚本；点击“关闭解析”后回到手动草稿模式，手写模式下切换脚本类型会自动清空配方格和流体行。上方“配方列表”会列出当前脚本类型下所有可解析配方，显示当前类型序号、行号、类型和更完整的摘要，例如 `输出 <- 输入` 或 `recipe map: 输入 -> 输出`；点击某一行会直接解析到 GUI。“第一条 / 上一条 / 下一条 / 最后一条”也可以在当前脚本类型的可解析配方之间切换。

右侧 ZS 预览分为上下两半：上半区是完整 `.zs` 文件编辑区，下半区是当前草稿生成内容。当前草稿会自动在脚本前写一行中文注释，例如 `// 木板 <minecraft:planks> * 2 和 煤炭 <minecraft:coal> * 3 有序合成 火把 <minecraft:torch> * 1`，GT 机器会生成类似 `// 活塞 <minecraft:piston> * 3 和 水 <liquid:water> * 1000 通过 gt.recipe.assembler 合成 黏性活塞 <minecraft:sticky_piston> * 1` 的注释。“添加位置”可选择“文件末尾”“当前光标”或“当前配方后”，点击“添加到脚本”会把下半区内容插入到对应位置；解析过配方后，点击“替换原配方”会用当前草稿替换完整脚本里的原始配方片段；“保存”保存的是上半区完整文件，已有当前文件时不再弹出另存为窗口。两个区域都有竖向和横向滚动条，上半区支持“撤销”和“重做”。

点击“添加到脚本”或“替换原配方”前会先校验当前草稿；如果缺少输出、缺少输入、`Duration` / `EU/t` / `Special Value` 等数字字段非法，工具只会在下半区显示错误和状态提示，不会把 `// 无法生成脚本...` 写进完整脚本。保存完整 `.zs` 文件不会被当前草稿校验拦截，方便继续手写或修整完整脚本。

上方“草稿列表”可以临时保存多条当前草稿。点击“保存草稿”会把当前可生成的草稿加入列表，双击或选中后点击“载入草稿”会回填到 GUI；“删除草稿”会移除选中项；“全部添加”会按列表顺序把所有草稿追加到右侧上半区完整脚本。

## 输入

选择导出的物品索引，例如：

```text
D:\Code\gtnh_item_doc_exporter\item_index.json
```

如果同目录存在 `fluid_index.json`，GUI 会自动加载流体索引。GTNH/模组机器生成方式中的“流体输入”和“流体输出”都有独立的“条数”输入框，默认 1 条；填入几条就会生成几条对应的流体 UI 行。每行可以点击“搜索”，按中文名、`fluidName` 或 `<liquid:...>` 表达式查找流体，双击后填入当前流体行。

如果同目录存在 `ore_dictionary_index.json`，GUI 会自动加载矿物字典索引。先点击一个配方输入格，再点击工具栏的“填入 OreDict”，可以按 `oreName`、`<ore:...>` 表达式或包含的物品表达式搜索，双击后会把 `<ore:...>` 写入当前输入格。OreDict 只作为输入使用，不会填入输出格。

## 支持脚本

- 有序合成
- 镜像有序合成 `recipes.addShapedMirrored`
- 无序合成
- 熔炉配方
- 熔炉燃料 `furnace.setFuel`
- 删除配方
- GTNH / 模组机器配方
- 矿物字典输入 `<ore:...>`
- 物品数量 `*0` 和 `.withTag(...)` 后缀
- RA2 `.outputChances(...)` 输出概率
- RA2 `.specialValue(...)`
- RA2 `.specialItem(...)`
- RA2 `.noFluidInputs()` / `.noFluidOutputs()` 开关
- 导入 `.zs`、按当前脚本类型解析到 GUI、配方列表点击解析、脚本草稿列表、智能摘要、自动中文注释、解析模式下切换类型自动重解析、在当前类型配方间上一条/下一条导航、按位置添加草稿到完整脚本、替换原配方

不同脚本类型使用独立配方格界面：有序合成和无序合成为 `3 x 3` 输入加 1 个输出，熔炉为 1 个输入加 1 个输出，燃料为 1 个输入且无输出，GTNH/模组机器为 16 个物品输入加 9 个物品输出。机器生成方式支持流体输入/输出、`duration` 和 `EU/t`。其中 Thermal Expansion 与 AE 生成方式参考 ModTweaker 的 logger 输出；GT 机器使用统一的 `GT RA2` 生成方式，具体机器由 `Recipe Map` 决定，语法参考 Minetweaker-Gregtech-5-Addon Wiki 的 RA2 builder：

点击任意物品格后，中间的“选中物品格”区域可以编辑数量和后缀。数量允许 `0`，用于 GT 编程电路或模具这类 `<...> * 0` 输入；后缀会直接拼接到物品表达式之后，可填写 `.withTag(...)` 这类 NBT 表达式。GTNH/模组机器模式下选中输出格时，还可以填写“输出概率”，单位为 GT 常用的 `10000 = 100%`，会生成 RA2 的 `.outputChances([...])`。

删除模式下会显示“删除类型”子选项，可选择有序、无序、熔炉或 GT，并切换到对应的独立配方格界面。GT 删除使用 16 个物品输入格作为 `RecipeRemover.remove(...)` 的物品输入数组，并提供独立的“GT 删除流体输入”多行列表，每行都可搜索流体、填写数量或清空。

参数区提供 MineTweaker 常用选项：“镜像有序合成”会让有序合成生成 `recipes.addShapedMirrored(...)`；“写入熔炉 XP”关闭后，熔炉配方会生成两参数写法 `furnace.addRecipe(output, input);`；“燃烧时间”用于燃料模式生成 `furnace.setFuel(item, ticks);`。

参数和流体区会按脚本类型显示：有序/无序合成不显示流体，熔炉只显示 XP，燃料只显示燃烧时间，GTNH/模组机器显示“生成方式”、`Recipe Map`、`Duration`、`EU/t`、无流体开关和可调条数的流体输入/输出。删除模式只有选择 `GT` 时才显示 `Recipe Map` 和专用的 GT 删除流体输入列表。

GTNH/模组机器参数区的 `Special Value` 默认留空，不生成脚本；填入整数后会生成 `.specialValue(value)`。

GTNH/模组机器参数区的 `Special Item` 默认留空，不生成脚本；先选中一个已有物品的配方格，再点击“从当前选中物品填入”，会复制该物品的表达式、数量和后缀，并生成 `.specialItem(item)`。

GUI 的第一 UI 优先级是保持当前三栏比例：左侧物品搜索栏固定宽度，右侧 ZS 预览固定宽度，中间编辑区使用剩余空间。默认窗口为 `1500 x 1080`，旧保存配置的高度低于 `1040` 时会自动提升；后续新增控件时必须先保证这个比例不被破坏；上方“配方列表”和“草稿列表”行数保持固定，增加出来的高度优先给下面左侧搜索、中间编辑和右侧预览三栏；左侧、中间和右侧长内容依靠各自滚动条查看，不允许撑宽侧栏挤压中间编辑区。顶部工具栏使用两排按钮，“选择 item_index.json”保留完整文字；按钮按中文显示宽度预留空间，避免文字被挤压。

GTNH/模组机器模式下，“生成方式”只决定脚本生成语法，当前保留 `GT RA2`、`Thermal Expansion Furnace`、`Thermal Expansion Pulverizer`、`AE Grinder` 和 `AE Inscriber`。`Recipe Map` 下拉框决定 GT 配方真正加入哪张配方表；列表来自 Wiki 的 `Available recipe maps`，界面会显示中文名和原 ID，例如 `组装机 (gt.recipe.assembler)`；选择后会覆盖 `GT RA2` 的默认 recipe map，生成脚本时仍使用括号中的原 ID。旧配置里的 `assembler_like`、`cutter_like` 等旧模板 ID 会自动迁移到 `GT RA2`，并保留原先对应的默认 `Recipe Map`。参数区的“无流体输入”和“无流体输出”会生成 RA2 的 `.noFluidInputs()` / `.noFluidOutputs()`，并跳过对应的 `.fluidInputs(...)` / `.fluidOutputs(...)`。

```zenscript
mods.gregtech.RA2
    .builder()
    .itemInputs([<minecraft:dirt>])
    .itemOutputs([<minecraft:obsidian>])
    .duration(420)
    .eut(100)
    .addTo("gt.recipe.assembler");
```

删除 GT 机器配方时可在“删除模式”选择 `GT`，会生成：

```zenscript
mods.gregtech.RecipeRemover.remove("gt.recipe.assembler", [<minecraft:piston>, <minecraft:slime_ball>], []);
```

如果填写多条 GT 删除流体输入，会生成同一个流体数组参数：

```zenscript
mods.gregtech.RecipeRemover.remove("gt.recipe.assembler", [<minecraft:piston>], [<liquid:water> * 1000, <liquid:chlorine> * 144]);
```

## 打包

```powershell
.\build.bat
```

应用窗口和打包后的 exe 使用项目目录下的 `icon.ico` 作为图标。
