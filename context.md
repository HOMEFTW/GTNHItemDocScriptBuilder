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
| 中间配方编辑 | `gui.main_window.MainWindow` | 已支持有序、无序、熔炉、删除、GTNH/模组机器布局 |
| 右侧 ZS 预览 | `gui.widgets.PreviewFrame` | 已支持横向和竖向滚动条 |
| 流体搜索 | `gui.widgets.FluidSearchDialog` | 已支持流体输入/输出行搜索填入 |
| OreDict 搜索 | `gui.widgets.OreDictionarySearchDialog` | 已支持 `<ore:...>` 搜索并填入当前输入格 |

### Layout Contract
- 左侧搜索栏固定宽度：`SEARCH_PANE_WIDTH = 580`
- 右侧预览栏固定宽度：`PREVIEW_PANE_WIDTH = 400`
- 中间编辑区使用剩余空间：`EDITOR_PANE_WEIGHT = 1`
- 后续新增控件必须优先保持该比例，长内容通过滚动条处理。

### Script Features
| Feature | Status |
|---------|--------|
| Shaped crafting | 已支持 |
| Shapeless crafting | 已支持 |
| Furnace recipe | 已支持 |
| Recipe removal layouts | 已支持有序、无序、熔炉、GT 子选项 |
| GTNH RA2 builder | 已支持基础 item/fluid inputs/outputs、duration、EU/t、recipe map |
| Ore dictionary inputs | 已支持输入格填入 |

## Dependencies
- Python
- Tkinter
- PyInstaller for packaging

## Architecture Notes
- GUI 使用独立桌面窗口，不使用浏览器或 localhost。
- OreDict、Fluid 和 Item 均作为导出索引读取，不在 GUI 内重新扫描 Minecraft。
- OreDict 填入逻辑只面向当前选中的输入格，避免生成非法输出表达式。
