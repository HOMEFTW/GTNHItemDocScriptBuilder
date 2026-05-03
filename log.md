# Development Log

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
