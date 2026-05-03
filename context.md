# Project Context

## Basic Info
- Project Name: GTNHItemDocScriptBuilder
- Type: Tkinter desktop GUI
- Purpose: 使用 `GTNHItemDocExporter` 导出的索引生成 CraftTweaker / ModTweaker / GTNH `.zs` 脚本。
- Main Entry: `main.py`

## Implemented Content

### Data Sources
| File | Loader | Status |
|------|--------|--------|
| `item_index.json` | `core.item_index.ItemIndexStore` | 已支持 |
| `fluid_index.json` | `core.fluid_index.FluidIndexStore` | 已支持，自动从 `item_index.json` 同目录加载 |
| `ore_dictionary_index.json` | `core.ore_dictionary_index.OreDictionaryIndexStore` | 已支持，自动从 `item_index.json` 同目录加载 |

### GUI
| Area | Implementation | Status |
|------|----------------|--------|
| 左侧物品搜索 | `gui.widgets.ItemSearchFrame` | 已支持中文名、英文名、注册 ID 搜索，并带横向滚动条 |
| 中间配方编辑 | `gui.main_window.MainWindow` | 已支持有序、无序、熔炉、燃料、删除、GTNH/模组机器布局；GT 机器为 16 输入 + 9 输出 |
| 选中物品格编辑 | `gui.main_window.MainWindow` | 已支持数量 `0`、`.withTag(...)` 后缀，以及 GT 机器输出概率 |
| 右侧 ZS 预览 | `gui.widgets.PreviewFrame` | 已分为上下两半：完整 `.zs` 文件原文和当前草稿保存内容，两区均有横向和竖向滚动条 |
| 流体搜索 | `gui.widgets.FluidSearchDialog` | 已支持流体输入/输出行搜索填入 |
| GT 删除流体输入 | `gui.widgets.FluidListRowsFrame` | 已支持 4 行流体输入，每行可搜索、填写数量和清空 |
| OreDict 搜索 | `gui.widgets.OreDictionarySearchDialog` | 已支持 `<ore:...>` 搜索并填入当前输入格 |
| ZS 导入 | `core.zs_parser.parse_zs_script` + `MainWindow._load_draft` | 已支持导入第一条受支持配方并恢复到当前 GUI 草稿 |

### Layout Contract
- 左侧搜索栏固定宽度：`SEARCH_PANE_WIDTH = 580`
- 右侧预览栏固定宽度：`PREVIEW_PANE_WIDTH = 400`
- 中间编辑区使用剩余空间：`EDITOR_PANE_WEIGHT = 6`
- 参数区内 MineTweaker 选项使用左侧纵向排列，避免被 `Recipe Map` 宽列推到右边。
- MineTweaker 专项参数按脚本类型显隐：`shaped_mirrored` 仅有序合成，`include_furnace_xp` 仅熔炉，`fuel_ticks` 仅燃料。
- 参数和流体区按能力显隐：合成/熔炉/燃料不显示 GT 流体区，机器显示流体输入/输出，GT 删除只显示流体输入。
- 中间编辑栏使用竖向滚动容器，新增控件不能通过撑高窗口来解决可见性问题。
- 默认窗口：`1500 x 920`
- 最小窗口：`1400 x 900`
- 后续新增控件必须优先保持该比例，长内容通过滚动条处理。

### Script Features
| Feature | Status |
|---------|--------|
| Shaped crafting | 已支持 |
| Mirrored shaped crafting | 已支持，参数区“镜像有序合成”生成 `recipes.addShapedMirrored(...)` |
| Shapeless crafting | 已支持 |
| Furnace recipe | 已支持，可选择是否写入 XP 参数 |
| Furnace fuel | 已支持，生成 `furnace.setFuel(item, ticks)` |
| Recipe removal layouts | 已支持有序、无序、熔炉、GT 子选项 |
| GT RecipeRemover | 已支持 `RecipeRemover.remove(recipeMap, itemInputs, fluidInputs)`，物品输入来自 16 格，流体输入来自独立 4 行列表 |
| GTNH RA2 builder | 已支持基础 item/fluid inputs/outputs、outputChances、specialValue、specialItem、duration、EU/t、recipe map、无流体输入/输出开关 |
| `.zs` import/re-edit | 已支持本工具生成的 RA2、GT 删除、合成、熔炉、燃料脚本导入回填 |
| Ore dictionary inputs | 已支持输入格填入 |
| Item amount `*0` | 已支持 |
| Item suffix / NBT `.withTag(...)` | 已支持原样拼接 |

## Dependencies
- Python
- Tkinter
- PyInstaller for packaging

## Architecture Notes
- GUI 使用独立桌面窗口，不使用浏览器或 localhost。
- OreDict、Fluid 和 Item 均作为导出索引读取，不在 GUI 内重新扫描 Minecraft。
- OreDict 填入逻辑只面向当前选中的输入格，避免生成非法输出表达式。
- 物品后缀不做语法解析，作为原始 CraftTweaker 片段保存在 `ScriptItem.suffix`。
- RA2 输出概率使用 GregTech 常用单位 `10000 = 100%`，只在 GTNH/模组机器输出格上编辑和生成。
- RA2 `specialValue` 为可选整数，空值时不生成 `.specialValue(...)`。
- RA2 `specialItem` 复制现有 `ScriptItem`，保留数量 `*0` 和 `.withTag(...)` 后缀。
- 当前 Addon 源码 `RA2Builder.java` 暴露了 `noFluidInputs()` / `noFluidOutputs()`；Wiki 提到的 `noOptimize()` 未在当前源码中找到，暂不生成。
- GT 删除模式不复用普通机器流体输入控件，避免只有一条流体输入；`FluidListRowsFrame` 专门服务 `RecipeRemover.remove(...)` 的流体数组参数。
- `.zs` 导入是 MVP 级静态解析：不执行 ZenScript，只解析第一条匹配的受支持配方，目标是让保存后的脚本在程序重启后能导入继续编辑。
- ZS 预览只代表当前一份草稿；脚本类型切换时会迁移当前格子到新布局，避免隐藏布局恢复旧草稿造成“不同类型不同预览”的错觉。
- `.zs` 导入按脚本出现顺序选择第一条受支持配方，不再用固定类型优先级抢先解析后面的调用。
- 右侧上半区保留完整导入文件，右侧下半区显示保存按钮会写出的当前草稿内容，并在标题中显示文件名、受支持配方序号、行号和调用类型。
