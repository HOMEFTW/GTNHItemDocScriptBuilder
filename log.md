# Development Log

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
