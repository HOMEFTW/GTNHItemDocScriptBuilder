# Project Context

## Basic Info
- Project Name: GTNHItemDocScriptBuilder
- Version: 1.0.0
- Studio: Andgatech
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
| 右侧 ZS 预览 | `gui.widgets.PreviewFrame` | 已分为上下两半：完整 `.zs` 文件编辑区和当前草稿保存内容，两区均有横向和竖向滚动条 |
| 流体搜索 | `gui.widgets.FluidSearchDialog` + `gui.widgets.FluidListRowsFrame` | 已支持 GT 机器流体输入/输出分别填写条数，动态生成对应 UI 行并搜索填入 |
| GT 删除流体输入 | `gui.widgets.FluidListRowsFrame` | 已支持 4 行流体输入，每行可搜索、填写数量和清空 |
| OreDict 搜索 | `gui.widgets.OreDictionarySearchDialog` | 已支持 `<ore:...>` 搜索并填入当前输入格 |
| ZS 导入 | `core.zs_parser.parse_zs_script_with_source` + `MainWindow._parse_current_script_to_gui` | 导入只加载完整脚本；点击“解析到GUI”后按当前脚本类型解析并恢复到 GUI 草稿，解析模式开启后切换类型会自动重解析，并支持当前类型上一条/下一条导航 |
| ZS 文件工作流 | `MainWindow._new_script` / `_save_script` / `_save_script_as` | 已支持未导入时新建 `.zs` 文件、绑定当前文件路径、保存直接覆盖当前文件、另存为切换当前文件 |
| 草稿校验 | `MainWindow._generate_current_draft_script` | `添加到脚本` 和 `替换原配方` 前会阻止无效草稿写入完整脚本，并在状态栏提示错误 |
| 草稿列表 | `MainWindow.saved_drafts` + `saved_draft_tree` | 已支持保存当前草稿、载入选中草稿、删除选中草稿、按顺序全部追加到完整脚本 |
| 应用图标 | `icon.ico` + `MainWindow._configure_icon` + `build.spec` | 窗口标题栏和 PyInstaller exe 均使用项目目录下的 `icon.ico` |
| 配方列表 | `core.zs_parser.parse_zs_script_matches` + `MainWindow.recipe_match_tree` | 已支持按当前脚本类型列出所有可解析配方，显示序号、行号、类型和智能摘要，点击行可直接解析到 GUI |
| 脚本编辑安全 | `ParsedRecipe.start_offset/end_offset` + `MainWindow._replace_current_recipe` | 已支持添加位置选择：文件末尾、当前光标、当前配方后；已支持替换当前解析配方的原始脚本片段 |
| 自动注释 | `MainWindow._draft_comment` | 当前草稿预览会自动生成中文说明注释，合成显示输入/输出，GT 显示输入、流体、recipe map 和输出 |
| 生成方式 | `core.templates.template_label_options` | 已简化为 `GT RA2`、`Thermal Expansion Furnace`、`Thermal Expansion Pulverizer`、`AE Grinder`、`AE Inscriber`；GT 具体机器由 `Recipe Map` 决定 |
| 关于对话框 | `gui.dialogs.AboutDialog` + `MainWindow.about_button` | 已在窗口右上角提供“关于”按钮，显示应用名、版本 `1.0.0`、工作室 `Andgatech` 和用途说明 |

### Layout Contract
- 左侧搜索栏固定宽度：`SEARCH_PANE_WIDTH = 580`
- 右侧预览栏固定宽度：`PREVIEW_PANE_WIDTH = 400`
- 中间编辑区使用剩余空间：`EDITOR_PANE_WEIGHT = 6`
- 参数区内 MineTweaker 选项使用左侧纵向排列，避免被 `Recipe Map` 宽列推到右边。
- MineTweaker 专项参数按脚本类型显隐：`shaped_mirrored` 仅有序合成，`include_furnace_xp` 仅熔炉，`fuel_ticks` 仅燃料。
- 参数和流体区按能力显隐：合成/熔炉/燃料不显示 GT 流体区，机器显示流体输入/输出，GT 删除只显示流体输入。
- GT 机器普通流体输入和流体输出各自使用独立“条数”输入框，默认 1 条；填入几条就生成几条对应 UI 行。
- 中间编辑栏使用竖向滚动容器，新增控件不能通过撑高窗口来解决可见性问题。
- 顶部工具栏使用两排按钮；“选择 item_index.json”保留完整文字，中文按钮按显示宽度预留空间，不能把文字压到难以辨认。
- 默认窗口：`1500 x 1080`
- 最小窗口：`1400 x 1040`
- 上方“配方列表”和“草稿列表”高度固定，窗口新增高度分配给下面左侧搜索、中间编辑和右侧预览三栏。
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
| `.zs` import/re-edit | 已支持本工具生成的 RA2、GT 删除、合成、熔炉、燃料脚本按当前脚本类型解析回填；解析模式开启时切换类型自动按当前类型重解析，并可在当前类型匹配配方间跳转 |
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
- 机器参数区的“模板”已改名为“生成方式”；GT 只保留 `GT RA2`，不再显示 `Assembler-like`、`Cutter-like` 等重复模板，具体机器全部通过 `Recipe Map` 选择。
- 旧配置或旧草稿中出现的 `assembler_like`、`cutter_like`、`macerator_like`、`mixer_like`、`chemical_reactor_like`、`blast_furnace_like` 会归一化为 `generic_gt_machine`，同时保留旧模板对应的默认 `Recipe Map`。
- 当前 Addon 源码 `RA2Builder.java` 暴露了 `noFluidInputs()` / `noFluidOutputs()`；Wiki 提到的 `noOptimize()` 未在当前源码中找到，暂不生成。
- GT 删除模式不复用普通机器流体输入控件，避免只有一条流体输入；`FluidListRowsFrame` 专门服务 `RecipeRemover.remove(...)` 的流体数组参数。
- `.zs` 导入是 MVP 级静态解析：不执行 ZenScript；导入只打开完整文件，点击“解析到GUI”后只按当前脚本类型解析第一条匹配的受支持配方，并开启解析模式。
- ZS 预览只代表当前一份草稿；解析模式开启时切换脚本类型会重新按完整脚本和当前类型解析，避免把有序/无序草稿误迁移成 GT 草稿；点击“关闭解析”后才使用手动草稿迁移。
- 手写模式下切换“脚本类型”会清空所有配方格和流体行，避免上一个脚本类型的格子误带入新类型；解析模式下仍按当前类型自动重新解析。
- `.zs` 解析按当前脚本类型过滤后，再按脚本出现顺序选择受支持配方；解析导航按钮维护当前类型游标，支持“第一条 / 上一条 / 下一条 / 最后一条”，配方列表则展示同一过滤结果并可点击跳转。
- 右侧上半区是完整脚本编辑区；“添加到脚本”按“添加位置”插入当前草稿，支持文件末尾、当前光标、当前配方后；“替换原配方”使用 parser 返回的字符 offset 替换原始配方片段；“保存 .zs”保存上半区完整文件。
- 未导入 `.zs` 时可以点击“新建 .zs”先创建空脚本并绑定当前文件；导入或新建后“保存”直接覆盖当前文件，未绑定路径时“保存”会自动走“另存为”；“另存为”会切换当前文件路径。
- “添加到脚本”和“替换原配方”使用同一个草稿生成/校验路径；当当前草稿缺输入/输出或数字字段非法时只更新下半区错误预览和状态栏，不修改右侧上半区完整脚本。
- 草稿列表保存在当前 GUI 会话内，使用 `deepcopy(RecipeDraft)` 保存当时状态；目前不写入磁盘，关闭程序后清空。
- 下半区当前草稿会自动追加中文注释行；有中文名时使用 `中文名 <ct表达式> * 数量`，没有中文名时回退到 CT 表达式或流体名。
- 上半区支持撤销和重做，面向完整脚本编辑。
