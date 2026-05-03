# Development Log

## 2026-05-03: RA2 输出概率支持

### Completed
- 为 `RecipeDraft` 增加 `output_chances`。
- GTNH/模组机器生成器支持 `.outputChances([...])`，未填写概率时保持旧脚本格式不变。
- 输出格保存独立 `output_chance`，默认 `10000` 表示 `100%`。
- GUI 在 GTNH/模组机器模式下选中输出格时显示“输出概率”，选中输入格或其他脚本类型时隐藏。
- 补充生成器和 GUI 测试。

### Issues Encountered
- **输出概率只对 GT RA2 输出有效**：普通合成、熔炉和输入格不应显示该控件 → 显隐绑定到“机器模式 + 当前选中输出格”。

### Decisions Made
- 使用 GregTech 常用概率单位 `10000 = 100%`，不做百分号换算，避免和真实 `.zs` 脚本数值不一致。

---

## 2026-05-03: 参数和流体区按能力显示

### Completed
- 有序/无序合成不再显示流体输入/输出、模板、`Recipe Map`、`Duration`、`EU/t` 等无效参数。
- 熔炉只显示 XP 相关参数，燃料只显示燃烧时间。
- GTNH/模组机器显示模板、`Recipe Map`、`Duration`、`EU/t`、无流体开关和流体输入/输出。
- 删除模式仅在子类型为 `GT` 时显示模板、`Recipe Map` 和流体输入；普通有序/无序/熔炉删除不显示流体。
- 补充 GUI 测试，锁定各脚本类型的参数与流体显隐规则。

### Issues Encountered
- **有序/无序显示流体输入输出**：这些脚本语法根本不接收流体 → 将流体区限制到机器配方和 GT 删除。

### Decisions Made
- 隐藏控件时保留已填值，切换回对应类型后仍可继续编辑。

---

## 2026-05-03: MineTweaker 参数按类型显示

### Completed
- 将 MineTweaker 专项参数改为按脚本类型显示。
- 有序合成只显示“镜像有序合成”，无序合成不显示这些专项参数。
- 熔炉只显示“写入熔炉 XP”，燃料只显示“燃烧时间”。
- 补充 GUI 测试，锁定参数显隐行为。

### Issues Encountered
- **公共参数区误导性强**：`recipes.addShapedMirrored`、`furnace.addRecipe` XP 开关和 `furnace.setFuel` ticks 并不适用于所有类别 → 根据 `recipe_kind` 控制显隐。

### Decisions Made
- 保留参数值本身，不因切换类别清空；只控制显示，避免用户临时切换类型时丢配置。

---

## 2026-05-03: MineTweaker 参数左对齐

### Completed
- 将“写入熔炉 XP”、“镜像有序合成”和“燃烧时间”从参数区右侧列移动到左侧连续行。
- 增加 GUI 布局测试，约束 MineTweaker 参数控件从第 0 列开始，避免被 `Recipe Map` 宽列推远。

### Issues Encountered
- **新控件离左侧太远**：控件放在第 2/3 列，受 `Recipe Map` 下拉框宽度影响 → 改为左侧纵向排列。

### Decisions Made
- 不改变三栏比例常量，只调整参数框内部 grid 排列。

---

## 2026-05-03: MineTweaker 合成与熔炉补充

### Completed
- 为 `RecipeDraft` 增加 `shaped_mirrored`、`include_furnace_xp` 和 `fuel_ticks`。
- 生成器支持 `recipes.addShapedMirrored(...)`、两参数 `furnace.addRecipe(output, input)` 和 `furnace.setFuel(item, ticks)`。
- GUI 脚本类型增加“燃料”，布局为 1 个输入格、无输出格。
- 参数区增加“镜像有序合成”、“写入熔炉 XP”和“燃烧时间”控件。
- 补充生成器、布局和 GUI 测试，保持左侧 `580px`、右侧 `400px` 的三栏比例常量不变。

### Issues Encountered
- **真实脚本存在两参数熔炉写法**：原生成器固定输出 XP 参数 → 增加 `include_furnace_xp` 开关。

### Decisions Made
- “燃料”作为独立脚本类型处理，避免和熔炉配方共用输出格造成误填。

---

## 2026-05-03: RA2 无流体输入输出开关

### Completed
- 参考 `Minetweaker-Gregtech-5-Addon` Wiki 和源码 `RA2Builder.java`，核对 RA2 builder 可用方法。
- 为 `RecipeDraft` 增加 `no_fluid_inputs` 和 `no_fluid_outputs`。
- 在 GTNH/模组机器参数区增加“无流体输入”和“无流体输出”复选框。
- 勾选后生成 `.noFluidInputs()` / `.noFluidOutputs()`，并跳过对应的 `.fluidInputs(...)` / `.fluidOutputs(...)`。
- 补充生成器和 GUI 测试。

### Issues Encountered
- **Wiki 与当前源码不完全一致**：Wiki 文档列出 `.noOptimize()`，但当前 `RA2Builder.java` 未暴露该 `@ZenMethod` → 暂不让 GUI 生成 `.noOptimize()`。

### Decisions Made
- 先支持源码确认存在的 `.noFluidInputs()` 和 `.noFluidOutputs()`，保证生成脚本可用。
- 保持三栏比例不变；新增复选框放入中间参数区。

---

## 2026-05-03: 增加 GUI 窗口高度

### Completed
- 将默认窗口从 `1500x860` 调整为 `1500x920`。
- 将主窗口最小高度从 `760` 调整为 `900`。
- 将旧配置归一化的默认最小高度调整为 `900`，避免 `config.json` 中保存的 `1200x820` 继续让窗口偏矮。
- 更新窗口高度相关测试和文档。

### Issues Encountered
- **旧配置会覆盖默认窗口高度**：`config.json` 里保存了较矮窗口尺寸 → 通过提高 `normalize_window_geometry` 的 `min_height` 解决。

### Decisions Made
- 只增加高度，不调整左侧 `580px`、右侧 `400px` 和中间栏权重，继续保护既定三栏比例。

---

## 2026-05-03: 物品数量和 NBT 后缀支持

### Completed
- 为 `ScriptItem` 增加 `suffix` 字段，生成脚本时会拼接到物品表达式后，再追加数量。
- 调整物品数量生成逻辑，允许 `amount = 0` 输出 `<...> * 0`，用于 GT 编程电路和模具。
- 在中间编辑区增加“选中物品格”控件，可编辑当前格子的数量和 `.withTag(...)` 等后缀。
- 补充 `*0`、NBT 后缀和 GUI 选中格编辑行为测试。

### Issues Encountered
- **旧逻辑把 `0` 当作未设置数量**：`if self.amount and self.amount > 1` 会吞掉 `0` → 改为 `amount != 1` 时输出数量。

### Decisions Made
- 后缀只做原样拼接：GUI 不解析 NBT 内容，避免破坏 CraftTweaker 的原始表达式。
- 数量和后缀编辑放在中间栏内部：不改变左侧 `580px` 和右侧 `400px` 的固定比例。

---

## 2026-05-03: OreDict GUI 适配

### Completed
- 为 GUI 增加 `ore_dictionary_index.json` 自动加载流程，和 `item_index.json`、`fluid_index.json` 放在同一导出目录时会自动启用。
- 新增 OreDict 搜索弹窗，可按 `oreName`、`<ore:...>` 表达式和包含物品表达式搜索，并填入当前配方输入格。
- 补充 OreDict 索引、弹窗和主窗口填入行为测试。
- 保持三栏 UI 比例不变：左侧搜索 `580px`，右侧预览 `400px`，中间编辑区使用剩余空间。

### Issues Encountered
- **项目缺少 `log.md` 和 `context.md`**：本次按项目记录规则补齐，便于后续继续接力。

### Decisions Made
- OreDict 仅允许填入输入格：CraftTweaker 和 GregTech 配方输出通常需要具体物品，矿物字典更适合作为输入匹配。
- OreDict 搜索结果使用独立弹窗和横向滚动条：避免长物品列表撑宽主界面，保护既定三栏比例。
