# GTNHItemDocScriptBuilder GUI 设计

## 背景

`GTNHItemDocExporter` 已能在游戏内从 NEI 索引导出 `item_index.json`、`item_index.csv`、`item_index.md` 和 `last_export.log`。用户已从实际 GTNH 客户端生成 `D:\Code\gtnh_item_doc_exporter`，其中 `item_index.json` 包含 57232 条条目，`failureCount=0`。

第二阶段目标是创建一个独立桌面 GUI，用鼠标选择物品、填写配方格和参数，自动生成 CraftTweaker / ModTweaker `.zs` 脚本。GUI 必须参考 `D:\Code\gtnh-mod-installer` 的架构，而不是使用 Web/localhost。

## 参考项目

### `gtnh-mod-installer`

GUI 项目采用与 `gtnh-mod-installer` 相同的基本结构：

- `main.py` 作为入口。
- `gui/` 放主窗口、弹窗和可复用控件。
- `core/` 放业务逻辑和数据模型。
- `utils/` 放 JSON、路径、日志等通用工具。
- `build.bat` 和 `build.spec` 用于 PyInstaller 打包。
- UI 使用 Python `tkinter` / `ttk`，不依赖浏览器和本地服务端。

### `CraftTweaker-master`

基础脚本语法以 CraftTweaker 源码中的 API 为准：

- `recipes.addShaped(output, ingredients)`
- `recipes.addShapeless(output, ingredients)`
- `recipes.remove(output)`
- `recipes.removeShaped(output)`
- `recipes.removeShapeless(output)`
- `furnace.addRecipe(output, input, xp)`
- `furnace.remove(output, input)`

### `ModTweaker-master`

模组机器配方生成参考 ModTweaker 的 handler/logger 思路。ModTweaker 中每类机器会通过 logger 输出可复制的 ZS 语句，例如：

- `mods.thermalexpansion.Furnace.addRecipe(energy, input, output);`
- `mods.thermalexpansion.Pulverizer.addRecipe(energy, input, output, secondary, chance);`
- `mods.appeng.Grinder.addRecipe(input, output, energy, optional1, chance1, optional2, chance2);`
- `mods.appeng.Inscriber.addRecipe(inputs, top, bottom, output, mode);`

GUI 不把所有机器语法硬编码到窗口逻辑里，而是使用模板系统表达不同机器的参数顺序、字段名和输出格式。

## 项目位置

新建独立项目：

```text
D:\Code\GTNHItemDocScriptBuilder
```

不放入 `GTNHItemDocExporter` Java mod 仓库，避免桌面工具和 Forge mod 混在一起。

## 范围

第一版 GUI 同时覆盖 A、B、C：

- A：有序合成、无序合成、删除物品配方。
- B：熔炉配方，包含 XP。
- C：GTNH/模组机器模板，第一版支持 16 个物品输入、4 个物品输出、流体输入/输出、`duration`、`EU/t`。

第一版不实现配方索引反查，不直接读取游戏内已有配方，也不尝试在 GUI 中执行 CraftTweaker 脚本。GUI 只负责读取导出的物品索引、辅助编辑和生成 `.zs` 文本。

## 目录结构

```text
GTNHItemDocScriptBuilder/
  main.py
  requirements.txt
  build.bat
  build.spec
  config.json
  core/
    __init__.py
    item_index.py
    recipe_model.py
    script_project.py
    templates.py
    zs_generator.py
  gui/
    __init__.py
    dialogs.py
    main_window.py
    widgets.py
  utils/
    __init__.py
    helpers.py
    logger.py
  tests/
    test_item_index.py
    test_zs_generator.py
```

## 数据模型

### 物品索引

`core.item_index` 读取 `item_index.json` 并转换为轻量模型：

```text
ItemEntry
  mod_id
  registry_id
  meta
  ct_expression
  chinese_name
  english_name
  unlocalized_name
  is_block
  guid
  nbt_summary
```

搜索字段：

- 中文名
- 英文名
- 未本地化名
- `registryId`
- `ctExpression`
- `modId`

由于当前导出中英文名有较多 `item.*` / `tile.*` 回退，GUI 搜索和显示不能依赖英文名唯一可读；应优先显示中文名、`registryId` 和 `ctExpression`。

### 脚本元素

```text
ScriptItem
  expression
  amount
  comment_name

ScriptFluid
  name_or_expression
  amount

RecipeDraft
  kind
  item_inputs
  item_outputs
  fluid_inputs
  fluid_outputs
  duration
  eut
  xp
  remove_mode
  template_id
```

`ScriptItem.expression` 直接使用导出 JSON 中的 `ctExpression`。如果数量大于 1，则生成 `<mod:item> * amount`。

## GUI 设计

### 主窗口

窗口标题：

```text
GTNH 脚本生成器
```

主窗口分为三块：

- 左侧：物品索引搜索。
- 中间：配方编辑区。
- 右侧：ZS 预览和导出。

底部保留日志框和状态栏，沿用 `gtnh-mod-installer` 的 `LogFrame` / `StatusBar` 风格。

### 左侧物品索引

功能：

- 选择 `item_index.json`。
- 自动记住上次路径。
- 搜索框支持即时搜索。
- 表格列：中文名、英文名、CT 表达式、ID、meta、方块。
- 双击条目填入当前选中的配方格。
- 右键复制 CT 表达式。

性能要求：

- 57232 条索引加载后主窗口不应长时间无响应。
- 搜索使用内存索引和结果限制，默认显示前 500 条。
- 后续可加分页，但第一版先实现结果限制和状态提示。

### 中间配方编辑区

使用 `ttk.Notebook`：

#### 有序合成

- 3x3 输入格。
- 1 个输出格。
- 可设置输出数量。
- 生成 `recipes.addShaped(...)`。

#### 无序合成

- 9 个输入格。
- 1 个输出格。
- 可设置输出数量。
- 生成 `recipes.addShapeless(...)`。

#### 熔炉

- 1 个输入格。
- 1 个输出格。
- XP 数值框，默认 `0.0`。
- 生成 `furnace.addRecipe(output, input, xp)`。

#### 删除配方

- 目标物品格。
- 删除类型：全部、仅有序、仅无序、熔炉。
- 生成 `recipes.remove(...)`、`recipes.removeShaped(...)`、`recipes.removeShapeless(...)` 或 `furnace.remove(...)`。

#### GTNH/模组机器

- 模板下拉框。
- 16 个物品输入格。
- 4 个物品输出格。
- 流体输入列表。
- 流体输出列表。
- `duration` 数值框。
- `EU/t` 数值框。
- 生成模板定义的 ZS 语句。

第一版内置模板：

- `generic_gt_machine`
- `assembler_like`
- `cutter_like`
- `macerator_like`
- `mixer_like`
- `chemical_reactor_like`
- `blast_furnace_like`
- `thermal_expansion_furnace`
- `thermal_expansion_pulverizer`
- `appeng_grinder`
- `appeng_inscriber`

其中 GT 模板先作为可编辑模板输出器，不承诺所有 GTNH 机器已有统一 CraftTweaker 入口。这样可以先完成 GUI 闭环，再根据实际 GTNH/ModTweaker 可用语法逐个校准模板。

### 右侧 ZS 预览

功能：

- 实时显示当前草稿生成的 `.zs`。
- 按钮：复制、保存为 `.zs`、保存到 GTNH `scripts` 目录。
- 可设置脚本文件名，默认 `andgatech_recipes.zs`。
- 保存前做基础校验：输出不能为空、必要输入不能为空、数值字段必须有效。

## 模板系统

模板文件可放在 `core/templates.py` 或 `templates/*.json`。第一版为了简单和可测试，使用 Python 内置模板常量；后续再扩展为外部 JSON。

模板包含：

```text
id
display_name
max_item_inputs
max_item_outputs
max_fluid_inputs
max_fluid_outputs
fields
body
```

模板 body 使用占位符：

```text
{item_inputs}
{item_outputs}
{fluid_inputs}
{fluid_outputs}
{duration}
{eut}
```

示例输出风格：

```zenscript
// GTNH machine template: assembler_like
// 请根据当前 GTNH/ModTweaker 环境校准目标机器入口。
mods.gregtech.Assembler.addRecipe(
    [<minecraft:iron_ingot>, <minecraft:redstone>],
    [<minecraft:piston>],
    [],
    [],
    200,
    30
);
```

ModTweaker 已确认存在的模板可以输出更确定的语句，例如：

```zenscript
mods.thermalexpansion.Furnace.addRecipe(4000, <minecraft:sand>, <minecraft:glass>);
mods.appeng.Grinder.addRecipe(<minecraft:iron_ore>, <minecraft:iron_dust>, 4, null, 0, null, 0);
```

## 错误处理

- `item_index.json` 不存在：提示用户选择文件。
- JSON 格式错误：显示错误并保留旧索引。
- 索引版本不匹配：警告但允许继续。
- 保存路径无权限：提示错误，不吞掉异常。
- 配方草稿不完整：右侧预览显示校验信息，不生成误导性脚本。
- 模板字段缺失：提示模板错误。

## 配置

`config.json` 保存：

- 最近的 `item_index.json` 路径。
- 最近的 GTNH 客户端路径。
- 最近的脚本输出目录。
- 窗口大小。
- 最近选择的模板。

## 测试

第一版至少包含：

- `test_item_index.py`
  - 能读取真实结构的 `item_index.json`。
  - 能搜索中文、registry ID、CT 表达式。
  - 能限制搜索结果数量。

- `test_zs_generator.py`
  - 生成有序合成。
  - 生成无序合成。
  - 生成删除配方。
  - 生成熔炉配方。
  - 生成模板机器配方。
  - 空输出或无效数值会返回校验错误。

## 完成标准

- 能启动 GUI。
- 能加载 `D:\Code\gtnh_item_doc_exporter\item_index.json`。
- 能搜索 57232 条物品索引。
- 双击物品可填入当前选中的配方格。
- A、B、C 三类脚本都能生成 ZS 预览。
- 能保存 `.zs` 文件。
- 单元测试通过。
- 结构和打包方式与 `gtnh-mod-installer` 保持一致。
