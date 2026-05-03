# GTNHItemDocScriptBuilder

Tkinter 桌面工具，用 `GTNHItemDocExporter` 导出的 `item_index.json` 生成 CraftTweaker / ModTweaker `.zs` 脚本。

## 运行

```powershell
python main.py
```

## 输入

选择导出的物品索引，例如：

```text
D:\Code\gtnh_item_doc_exporter\item_index.json
```

如果同目录存在 `fluid_index.json`，GUI 会自动加载流体索引。GTNH/模组机器模板中的“流体输入”和“流体输出”可以点击“搜索”，按中文名、`fluidName` 或 `<liquid:...>` 表达式查找流体，双击后填入当前流体行。

## 支持脚本

- 有序合成
- 无序合成
- 熔炉配方
- 删除配方
- GTNH / 模组机器模板配方

不同脚本类型使用独立配方格界面：有序合成和无序合成为 `3 x 3` 输入加 1 个输出，熔炉为 1 个输入加 1 个输出，GTNH/模组机器为 16 个物品输入加 4 个物品输出。机器模板支持流体输入/输出、`duration` 和 `EU/t`。其中 Thermal Expansion 与 AE 模板参考 ModTweaker 的 logger 输出；GT 机器模板参考 Minetweaker-Gregtech-5-Addon Wiki 的 RA2 builder 语法：

删除模式下会显示“删除类型”子选项，可选择有序、无序、熔炉或 GT，并切换到对应的独立配方格界面。

GUI 会把过窄的历史窗口尺寸自动调整到适合三栏布局的宽度；中间编辑区拥有更高的 pane 权重，配方格按钮也做了紧凑化，避免 4 列机器格被遮住。

GTNH/模组机器模式下，“模板”下方有 `Recipe Map` 下拉框。列表来自 Wiki 的 `Available recipe maps`，界面会显示中文名和原 ID，例如 `组装机 (gt.recipe.assembler)`；选择后会覆盖模板默认 recipe map，生成脚本时仍使用括号中的原 ID。

```zenscript
mods.gregtech.RA2
    .builder()
    .itemInputs([<minecraft:dirt>])
    .itemOutputs([<minecraft:obsidian>])
    .duration(420)
    .eut(100)
    .addTo("gt.recipe.assembler");
```

删除 GT 机器配方时可在“删除模式”选择 `machine`，会生成：

```zenscript
mods.gregtech.RecipeRemover.remove("gt.recipe.assembler", [<minecraft:piston>, <minecraft:slime_ball>], []);
```

## 打包

```powershell
.\build.bat
```
