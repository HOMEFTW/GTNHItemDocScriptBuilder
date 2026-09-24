# Project Context

## Basic Info
- Project Name: GTNHItemDocScriptBuilder
- Version: 1.2.0
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
| 脚本与生成预览 | `gui.widgets.PreviewFrame` | 脚本编辑页显示完整文件；配方设计页显示只读生成预览，两区均有横向和竖向滚动条 |
| 流体搜索 | `gui.widgets.FluidSearchDialog` + `gui.widgets.FluidListRowsFrame` | 已支持 GT 机器流体输入/输出分别填写条数，动态生成对应 UI 行并搜索填入 |
| GT 删除流体输入 | `gui.widgets.FluidListRowsFrame` | 已支持 4 行流体输入，每行可搜索、填写数量和清空 |
| OreDict 搜索 | `gui.widgets.OreDictionarySearchDialog` | 已支持 `<ore:...>` 搜索并填入当前输入格 |
| ZS 导入 | `core.zs_parser.parse_zs_script_with_source` + `MainWindow._parse_current_script_to_gui` | 打开文件加载完整脚本并更新导航；脚本页“解析到GUI”按光标识别类型，设计页“按类型解析”恢复指定类型草稿，解析模式开启后切换类型会自动重解析，并支持当前类型上一条/下一条导航 |
| ZS 文件工作流 | `MainWindow._new_script` / `_save_script` / `_save_script_as` | 新建未命名缓冲区，首次保存选路径，保存直接覆盖当前文件，另存为切换路径，并有未保存保护 |
| 草稿校验 | `MainWindow._generate_current_draft_script` | `添加到脚本` 和 `替换原配方` 前会阻止无效草稿写入完整脚本，并在状态栏提示错误 |
| 草稿列表 | `MainWindow.saved_drafts` + `saved_draft_tree` | 已支持保存当前草稿、载入选中草稿、删除选中草稿、按顺序全部追加到完整脚本 |
| 应用图标 | `icon.ico` + `MainWindow._configure_icon` + `build.spec` | 窗口标题栏和 PyInstaller exe 均使用项目目录下的 `icon.ico` |
| 配方列表 | `core.zs_parser.parse_zs_script_matches` + `MainWindow.recipe_match_tree` | 已支持按当前脚本类型列出所有可解析配方，显示序号、行号、类型和智能摘要，点击行可直接解析到 GUI |
| 脚本编辑安全 | `ParsedRecipe.start_offset/end_offset` + `MainWindow._replace_current_recipe` | 已支持添加位置选择：文件末尾、当前光标、当前配方后；已支持替换当前解析配方的原始脚本片段 |
| 自动注释 | `MainWindow._draft_comment` | 当前草稿预览会自动生成中文说明注释，合成显示输入/输出，GT 显示输入、流体、recipe map 和输出 |
| 生成方式 | `core.templates.template_label_options` | 已简化为 `GT RA2`、`Thermal Expansion Furnace`、`Thermal Expansion Pulverizer`、`AE Grinder`、`AE Inscriber`；GT 具体机器由 `Recipe Map` 决定 |
| 关于对话框 | `gui.dialogs.AboutDialog` + `MainWindow.about_button` | 已在窗口右上角提供“关于”按钮，显示应用名、版本 `1.2.0`、工作室 `Andgatech` 和用途说明 |

### 工作区布局（2026-09-24 更新）
- GTNH 基线：`2.9.0-beta-3`。
- 左侧可调侧栏默认 `340px`，包含脚本目录与物品索引页签；主区域为脚本编辑与配方设计页签。
- 配方设计的表单和生成预览上下分区；底部配方导航与草稿暂存使用页签，所有主要分区可拖动。
- 默认窗口 `1440x900`，最小 `1000x700`，启动适配屏幕大小；不再保留旧三栏固定比例约束。
- 文件菜单、保存快捷键、未保存圆点、状态栏行列、就地查找与行号已实现。
- 新建使用内存缓冲区；打开/新建/退出有未保存保护，保存失败不切换文件。
- 脚本侧解析按光标识别类型，设计页仍支持按类型解析；过期配方 offset 禁止直接替换。

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
- `.zs` 导入是 MVP 级静态解析：不执行 ZenScript；打开只加载完整文件和导航；脚本页按光标识别类型，设计页支持当前类型过滤，解析成功后开启解析模式。
- ZS 预览只代表当前一份草稿；解析模式开启时切换脚本类型会重新按完整脚本和当前类型解析，避免把有序/无序草稿误迁移成 GT 草稿；点击“关闭解析”后才使用手动草稿迁移。
- 手写模式下切换“脚本类型”会清空所有配方格和流体行，避免上一个脚本类型的格子误带入新类型；解析模式下仍按当前类型自动重新解析。
- `.zs` 解析按当前脚本类型过滤后，再按脚本出现顺序选择受支持配方；解析导航按钮维护当前类型游标，支持“第一条 / 上一条 / 下一条 / 最后一条”，配方列表则展示同一过滤结果并可点击跳转。
- 中央脚本页是完整脚本编辑区；“添加到脚本”按“添加位置”插入当前草稿，支持文件末尾、当前光标、当前配方后；“替换原配方”使用 parser 返回的字符 offset 替换原始配方片段；“保存 .zs”保存脚本页完整文件。
- 未导入 `.zs` 时可以点击“新建 .zs”先创建未命名缓冲区，首次保存再绑定当前文件；导入或新建后“保存”直接覆盖当前文件，未绑定路径时“保存”会自动走“另存为”；“另存为”会切换当前文件路径。
- “添加到脚本”和“替换原配方”使用同一个草稿生成/校验路径；当当前草稿缺输入/输出或数字字段非法时只更新配方设计页错误预览和状态栏，不修改脚本编辑页完整脚本。
- 草稿列表保存在当前 GUI 会话内，使用 `deepcopy(RecipeDraft)` 保存当时状态；目前不写入磁盘，关闭程序后清空。
- 配方设计页当前草稿会自动追加中文注释行；有中文名时使用 `中文名 <ct表达式> * 数量`，没有中文名时回退到 CT 表达式或流体名。
- 脚本页支持撤销和重做，面向完整脚本编辑。

## GTNH 2.9.0-beta-3 兼容性核验
- manifest：NEI `2.8.130-GTNH`、CraftTweaker `3.4.8`、GT5 `5.09.54.133`、Minetweaker-Gregtech-5-Addon `2.3.4`、ModTweaker `0.14.0`。
- 已读取匹配的 GT Addon `2.3.4-dev.jar`，通过 `javap` 核验 `RA2Builder.builder/itemInputs/itemOutputs/noItemInputs/noItemOutputs/fluidInputs/fluidOutputs/noFluidInputs/noFluidOutputs/duration/eut/outputChances/specialValue/specialItem/addTo` 与 `RecipeRemover.remove(String, IIngredient[], IIngredient[])`。
- 现有核心生成语法不需要变更；未新增目标 jar 没有的 `noOptimize()`。
- 索引仍来自 Exporter 的现有 JSON 格式，不内置旧整合包物品列表。升级整合包后应重新导出。
- 未在 beta3 客户端加载生成脚本；静态 API 核验和 Python 测试不等于游戏执行验证，其他模组模板未逐一做目标 jar 核验。
