# GTNHItemDocScriptBuilder

面向 **GT New Horizons** 的桌面脚本工作区。读取 [GTNHItemDocExporter](https://github.com/HOMEFTW/GTNHItemDocExporter) 导出的索引，通过物品搜索、可视化配方设计和代码编辑，生成与维护 CraftTweaker / ModTweaker / GregTech `.zs` 脚本。

**应用版本：1.2.0 · 目标整合包：GTNH 2.9.0-beta-3 · 工作室：Andgatech**

[下载 Windows EXE](https://github.com/HOMEFTW/GTNHItemDocScriptBuilder/releases) · [下载配套导出器](https://github.com/HOMEFTW/GTNHItemDocExporter/releases) · [反馈问题](https://github.com/HOMEFTW/GTNHItemDocScriptBuilder/issues)

## 快速开始

1. 下载 [Releases](https://github.com/HOMEFTW/GTNHItemDocScriptBuilder/releases) 中面向 GTNH **2.9.0-beta-3** 的 `GTNHItemDocScriptBuilder.exe`。打包版无需另外安装 Python。
2. 在 GTNH 客户端使用 Exporter 生成索引。进入世界自动导出，或执行 `/itemdoc export`。
3. 运行编辑器，在左侧“物品索引”中点击“选择 item_index.json”。同目录的流体和矿物字典 JSON 会自动尝试加载。
4. 点击“新建 .zs”，或通过“打开 .zs / 打开文件夹”开始编辑已有脚本。
5. 在“配方设计”页选定类型，点击输入或输出格，再双击左侧物品填入；按需填写数量、流体和机器参数。
6. 检查生成预览，点击“添加到脚本”，然后按 **Ctrl+S** 保存。将需要使用的脚本放入对应游戏实例的 `scripts` 文件夹。

升级整合包后请重新导出索引，避免使用旧物品、流体或矿词数据。编辑器不会启动游戏或执行 ZenScript；实际配方效果需要在目标客户端验证。

## IDE 工作区

| 区域 | 用途 |
| --- | --- |
| 脚本目录 | 打开文件夹、递归浏览 `.zs`，双击或 Enter 打开文件 |
| 物品索引 | 搜索名称、注册 ID 与表达式，按物品/方块过滤 |
| 脚本编辑页 | 编辑完整文件，支持行号、语法高亮、就地查找和撤销/重做 |
| 配方设计页 | 编辑配方格、数量、NBT 后缀、机器参数及流体，查看只读生成预览 |
| 配方导航 | 查看受支持配方的类型、行号和摘要，选择配方继续编辑 |
| 草稿暂存 | 保存、载入、删除草稿，或按顺序全部添加到脚本 |
| 状态栏 | 查看操作结果、当前行列和文件编码提示 |

主要面板可拖动调整，菜单“视图 → 恢复面板布局”恢复侧栏与底部比例。默认窗口 `1440×900`，最小 `1000×700`，启动时根据屏幕大小调整。

当前是**单文档工作区**：脚本页和配方设计页对应同一个当前文件，不是多个文件的编辑页签。

## 文件与配方编辑流程

### 新建、打开和保存

“新建 .zs”先创建未命名缓冲区，首次保存时再选择文件路径。之后 Ctrl+S 直接保存当前文件；“另存为”会绑定新的路径。

文件有未保存内容时，标题与页签显示圆点。新建、打开其他文件或退出前，会提示保存、放弃或取消；保存失败或取消路径选择会保留当前内容。保存完整文件不受当前配方草稿是否有效影响。

### 从脚本继续编辑配方

打开脚本会更新配方导航，但不会自动覆盖当前 GUI 草稿。在脚本页点击“解析到GUI”，会识别光标附近的配方类型并切换到配方设计。也可以选择导航中的配方。

设计页的“按类型解析”支持按当前类型过滤，并在同类配方之间跳转。“关闭解析”使草稿恢复独立编辑；手动切换脚本类型会清空配方格。

### 生成、插入与替换

生成预览只表示当前草稿，**不会自动写入脚本或磁盘**。

- “添加到脚本”：插入到文件末尾、当前光标或已解析配方之后。
- “替换原配方”：替换当前解析的原始代码片段。
- 添加和替换前校验草稿；缺少输入、输出或参数非法时不会写入错误注释。
- 解析后如手写修改了完整脚本，应重新解析后再按配方位置插入或替换，避免使用过期位置。
- 最后点击“保存”或按 Ctrl+S，才会写入文件。

草稿暂存支持锁定参数，适合连续编写同类配方；**暂存只在当前会话有效，关闭程序后清空**。

## 支持的配方与参数

| 类别 | 支持内容 |
| --- | --- |
| 工作台 | 有序、镜像有序、无序合成 |
| 熔炉 | 熔炼配方、可选 XP、燃料燃烧时间 |
| 删除配方 | 工作台、熔炉、GT `RecipeRemover` |
| GT 机器 | RA2 builder、Recipe Map、物品/流体输入输出、Duration、EU/t |
| RA2 可选项 | 输出概率、Special Value、Special Item、无物品/无流体输入输出、单行格式 |
| 其他生成方式 | Thermal Expansion Furnace / Pulverizer、AE Grinder / Inscriber |

配方格支持数量 `0`，用于编程电路、模具等输入；物品后缀支持 `.withTag(...)` 等原始表达式。GT 输出概率使用 `10000 = 100%`。OreDict 只用于输入，可通过“填入 OreDict”搜索选择；流体列表可调整条数并逐行搜索。

“生成方式”选择语法，“Recipe Map”选择 GT 配方表。中文显示名不会改变生成代码中的原始 map ID。例如：

```zenscript
mods.gregtech.RA2
    .builder()
    .itemInputs([<minecraft:piston>, <minecraft:slime_ball>])
    .itemOutputs([<minecraft:sticky_piston>])
    .duration(200)
    .eut(30)
    .addTo("gt.recipe.assembler");
```

该片段用于展示语法，实际输入、输出与机器参数由使用者确定。

## 快捷键

| 操作 | 快捷键 |
| --- | --- |
| 新建 / 打开脚本 | Ctrl+N / Ctrl+O |
| 保存 / 另存为 | Ctrl+S / Ctrl+Shift+S |
| 查找 | Ctrl+F |
| 撤销 / 重做 | Ctrl+Z / Ctrl+Y |
| 添加当前配方 | Ctrl+G |
| 暂存当前草稿 | Ctrl+Shift+D |
| 上一条 / 下一条配方 | Alt+← / Alt+→ |

“全屏”打开独立编辑窗口，提供查找/替换；其中 Ctrl+H 打开替换。关闭时同步最后一次输入，“保存并关闭”实际写入文件，取消保存则继续停留在窗口。

## 从源码运行与打包

需要 **Python 3.10+** 和 Tkinter；本次在 Windows / Python 3.14 环境验证。

```powershell
git clone https://github.com/HOMEFTW/GTNHItemDocScriptBuilder.git
cd GTNHItemDocScriptBuilder
python main.py
```

运行时使用 Python 标准库。构建 Windows EXE 时安装打包依赖：

```powershell
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm build.spec
```

也可运行 `build.bat`。产物为 `dist/GTNHItemDocScriptBuilder.exe`。

执行测试：

```powershell
python -m unittest discover -s tests
```

部分测试会创建 Tk 窗口，需要可用的桌面环境。

## 验证范围与限制

- 本次覆盖原有 111 项测试和新增 16 项 IDE 回归，并完成 Windows 窗口检查与 EXE 打包。
- 已核验 GTNH beta3 对应的 Minetweaker-Gregtech-5-Addon `2.3.4` 中 RA2 与 RecipeRemover 接口。
- `.zs` 回填是静态解析，只支持已实现的配方语法；不执行脚本，不能保证任意手写函数、变量或宏均可回填。
- 尚未在 beta3 游戏中执行生成脚本；其他模组模板未逐一完成目标 jar 核验。

数据导出方式见 [GTNHItemDocExporter](https://github.com/HOMEFTW/GTNHItemDocExporter)。
