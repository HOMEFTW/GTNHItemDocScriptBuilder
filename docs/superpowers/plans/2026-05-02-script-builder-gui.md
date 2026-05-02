# GTNHItemDocScriptBuilder GUI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an independent Tkinter desktop GUI that loads `item_index.json` from GTNHItemDocExporter and generates CraftTweaker / ModTweaker `.zs` scripts for crafting, furnace, removal, and template-driven GTNH machine recipes.

**Architecture:** Follow `D:\Code\gtnh-mod-installer`: `main.py` entry point, `gui/` for Tkinter windows/widgets, `core/` for item index/search/model/script generation, `utils/` for JSON/log helpers, `tests/` for unit tests. Keep script generation pure and testable; the GUI only edits drafts and displays generated output.

**Tech Stack:** Python 3, standard-library `tkinter` / `ttk`, `unittest`, PyInstaller-compatible project files.

---

## File Map

- Create `main.py`: launches `gui.main_window.MainWindow`.
- Create `requirements.txt`: empty runtime dependencies except optional packaging note.
- Create `build.bat`: PyInstaller build command matching `gtnh-mod-installer`.
- Create `build.spec`: executable build definition.
- Create `config.json`: default paths and UI settings.
- Create `core/item_index.py`: load and search exported item index.
- Create `core/recipe_model.py`: dataclasses for items, fluids, and drafts.
- Create `core/templates.py`: built-in machine templates inspired by ModTweaker logger output.
- Create `core/zs_generator.py`: pure functions/classes that generate `.zs` text.
- Create `core/script_project.py`: save generated scripts and app config.
- Create `gui/main_window.py`: main Tkinter window and event wiring.
- Create `gui/widgets.py`: item search table, slot grids, fluid rows, preview frame.
- Create `gui/dialogs.py`: file/folder picker helpers and about dialog.
- Create `utils/helpers.py`: JSON and filesystem helpers.
- Create `utils/logger.py`: small stdout logger for status and diagnostics.
- Create `tests/test_item_index.py`: item index tests.
- Create `tests/test_zs_generator.py`: script generator tests.
- Create `tests/test_script_project.py`: config and script persistence tests.

---

### Task 1: Project Skeleton

**Files:**
- Create: `main.py`
- Create: `requirements.txt`
- Create: `build.bat`
- Create: `build.spec`
- Create: `config.json`
- Create: `core/__init__.py`
- Create: `gui/__init__.py`
- Create: `utils/__init__.py`
- Create: `utils/logger.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create baseline files**

`main.py`:

```python
#!/usr/bin/env python3
"""GTNH Item Doc Script Builder."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow


def main():
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
```

`requirements.txt`:

```text
pyinstaller>=6.0.0
```

`config.json`:

```json
{
  "item_index_path": "D:/Code/gtnh_item_doc_exporter/item_index.json",
  "gtnh_client_path": "",
  "script_output_dir": "",
  "window_geometry": "1200x820",
  "last_template": "generic_gt_machine"
}
```

`build.bat`:

```bat
@echo off
setlocal
cd /d "%~dp0"
python -m PyInstaller build.spec
endlocal
```

`build.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[("config.json", ".")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="GTNHItemDocScriptBuilder",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
```

`utils/logger.py`:

```python
"""Small logger helper matching the simple desktop-tool style."""
import datetime as _datetime


def log(message: str) -> str:
    line = f"[{_datetime.datetime.now().strftime('%H:%M:%S')}] {message}"
    print(line)
    return line
```

- [ ] **Step 2: Add temporary minimal GUI stub**

`gui/main_window.py`:

```python
"""Main window for GTNH Item Doc Script Builder."""
import tkinter as tk
from tkinter import ttk


class MainWindow:
    TITLE = "GTNH 脚本生成器"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(self.TITLE)
        self.root.geometry("1200x820")
        ttk.Label(self.root, text="GTNH 脚本生成器").pack(padx=20, pady=20)

    def run(self):
        self.root.mainloop()
```

- [ ] **Step 3: Smoke check import**

Run: `python -m unittest discover -v`

Expected: exits with 0 tests run and no import errors.

- [ ] **Step 4: Commit**

```bash
git add main.py requirements.txt build.bat build.spec config.json core gui utils tests
git commit -m "chore: scaffold script builder app"
```

---

### Task 2: Item Index Loading and Search

**Files:**
- Create: `core/item_index.py`
- Create: `utils/helpers.py`
- Test: `tests/test_item_index.py`

- [ ] **Step 1: Write failing tests**

`tests/test_item_index.py`:

```python
import json
import tempfile
import unittest
from pathlib import Path

from core.item_index import ItemIndexStore


class ItemIndexStoreTest(unittest.TestCase):
    def write_index(self, directory: Path) -> Path:
        path = directory / "item_index.json"
        path.write_text(json.dumps({
            "schemaVersion": 1,
            "generatedAt": "2026-05-02T21:46:40+0800",
            "minecraftVersion": "1.7.10",
            "language": "zh_CN",
            "entryCount": 3,
            "entries": [
                {
                    "modId": "minecraft",
                    "registryId": "minecraft:iron_ingot",
                    "meta": 0,
                    "ctExpression": "<minecraft:iron_ingot>",
                    "chineseName": "铁锭",
                    "englishName": "Iron Ingot",
                    "unlocalizedName": "item.ingotIron",
                    "isBlock": False,
                    "guid": "minecraft:iron_ingot:0",
                    "nbtSummary": ""
                },
                {
                    "modId": "minecraft",
                    "registryId": "minecraft:glass",
                    "meta": 0,
                    "ctExpression": "<minecraft:glass>",
                    "chineseName": "玻璃",
                    "englishName": "Glass",
                    "unlocalizedName": "tile.glass",
                    "isBlock": True,
                    "guid": "minecraft:glass:0",
                    "nbtSummary": ""
                },
                {
                    "modId": "gregtech",
                    "registryId": "gregtech:gt.metaitem.01",
                    "meta": 32700,
                    "ctExpression": "<gregtech:gt.metaitem.01:32700>",
                    "chineseName": "集成电路",
                    "englishName": "Integrated Circuit",
                    "unlocalizedName": "item.gt.integrated_circuit",
                    "isBlock": False,
                    "guid": "gregtech:gt.metaitem.01:32700",
                    "nbtSummary": ""
                }
            ]
        }), encoding="utf-8")
        return path

    def test_loads_entries_and_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ItemIndexStore.load(self.write_index(Path(tmp)))
            self.assertEqual(3, store.entry_count)
            self.assertEqual("zh_CN", store.language)
            self.assertEqual("<minecraft:iron_ingot>", store.entries[0].ct_expression)

    def test_searches_names_ids_and_ct_expressions(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ItemIndexStore.load(self.write_index(Path(tmp)))
            self.assertEqual(["minecraft:iron_ingot"], [e.registry_id for e in store.search("铁")])
            self.assertEqual(["minecraft:glass"], [e.registry_id for e in store.search("glass")])
            self.assertEqual(["gregtech:gt.metaitem.01"], [e.registry_id for e in store.search("32700")])

    def test_search_limits_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = ItemIndexStore.load(self.write_index(Path(tmp)))
            self.assertEqual(2, len(store.search("", limit=2)))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify failure**

Run: `python -m unittest tests.test_item_index -v`

Expected: FAIL with `ModuleNotFoundError` or missing `ItemIndexStore`.

- [ ] **Step 3: Implement item index loading**

`utils/helpers.py`:

```python
"""General helpers."""
import json
from pathlib import Path
from typing import Any, Dict


def load_json(path: str | Path) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: str | Path, data: Dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
```

`core/item_index.py`:

```python
"""Load and search GTNH item document exports."""
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from utils.helpers import load_json


@dataclass(frozen=True)
class ItemEntry:
    mod_id: str
    registry_id: str
    meta: int
    ct_expression: str
    chinese_name: str
    english_name: str
    unlocalized_name: str
    is_block: bool
    guid: str
    nbt_summary: str

    @classmethod
    def from_json(cls, data: dict) -> "ItemEntry":
        return cls(
            mod_id=str(data.get("modId", "")),
            registry_id=str(data.get("registryId", "")),
            meta=int(data.get("meta", 0)),
            ct_expression=str(data.get("ctExpression", "")),
            chinese_name=str(data.get("chineseName", "")),
            english_name=str(data.get("englishName", "")),
            unlocalized_name=str(data.get("unlocalizedName", "")),
            is_block=bool(data.get("isBlock", False)),
            guid=str(data.get("guid", "")),
            nbt_summary=str(data.get("nbtSummary", "")),
        )

    def search_text(self) -> str:
        return " ".join([
            self.mod_id,
            self.registry_id,
            str(self.meta),
            self.ct_expression,
            self.chinese_name,
            self.english_name,
            self.unlocalized_name,
            self.guid,
        ]).lower()


class ItemIndexStore:
    def __init__(self, entries: Iterable[ItemEntry], language: str = "", generated_at: str = ""):
        self.entries: List[ItemEntry] = list(entries)
        self.language = language
        self.generated_at = generated_at
        self.entry_count = len(self.entries)
        self._search_text = [(entry, entry.search_text()) for entry in self.entries]

    @classmethod
    def load(cls, path: str | Path) -> "ItemIndexStore":
        data = load_json(path)
        entries = [ItemEntry.from_json(item) for item in data.get("entries", [])]
        return cls(entries, str(data.get("language", "")), str(data.get("generatedAt", "")))

    def search(self, query: str, limit: int = 500) -> List[ItemEntry]:
        normalized = query.strip().lower()
        if not normalized:
            return self.entries[:limit]
        results: List[ItemEntry] = []
        terms = normalized.split()
        for entry, text in self._search_text:
            if all(term in text for term in terms):
                results.append(entry)
                if len(results) >= limit:
                    break
        return results
```

- [ ] **Step 4: Run tests**

Run: `python -m unittest tests.test_item_index -v`

Expected: PASS all 3 tests.

- [ ] **Step 5: Commit**

```bash
git add core/item_index.py utils/helpers.py tests/test_item_index.py
git commit -m "feat: load and search item index"
```

---

### Task 3: Recipe Models and ZS Generator

**Files:**
- Create: `core/recipe_model.py`
- Create: `core/templates.py`
- Create: `core/zs_generator.py`
- Test: `tests/test_zs_generator.py`

- [ ] **Step 1: Write failing generator tests**

`tests/test_zs_generator.py`:

```python
import unittest

from core.recipe_model import RecipeDraft, ScriptFluid, ScriptItem
from core.zs_generator import ZsGenerator


class ZsGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.generator = ZsGenerator()

    def item(self, expression, amount=1):
        return ScriptItem(expression=expression, amount=amount, comment_name="")

    def test_generates_shaped_recipe(self):
        draft = RecipeDraft(
            kind="shaped",
            item_inputs=[
                self.item("<minecraft:planks>"), self.item("<minecraft:planks>"), self.item("<minecraft:planks>"),
                self.item("<minecraft:planks>"), None, self.item("<minecraft:planks>"),
                self.item("<minecraft:planks>"), self.item("<minecraft:planks>"), self.item("<minecraft:planks>"),
            ],
            item_outputs=[self.item("<minecraft:chest>")],
        )
        script = self.generator.generate(draft)
        self.assertIn("recipes.addShaped(<minecraft:chest>,", script)
        self.assertIn("[<minecraft:planks>, null, <minecraft:planks>]", script)

    def test_generates_shapeless_recipe_with_amount(self):
        draft = RecipeDraft(
            kind="shapeless",
            item_inputs=[self.item("<minecraft:planks>")],
            item_outputs=[self.item("<minecraft:stick>", 4)],
        )
        self.assertEqual(
            "recipes.addShapeless(<minecraft:stick> * 4, [<minecraft:planks>]);",
            self.generator.generate(draft).strip(),
        )

    def test_generates_furnace_recipe(self):
        draft = RecipeDraft(
            kind="furnace",
            item_inputs=[self.item("<minecraft:sand>")],
            item_outputs=[self.item("<minecraft:glass>")],
            xp=0.0,
        )
        self.assertEqual(
            "furnace.addRecipe(<minecraft:glass>, <minecraft:sand>, 0.0);",
            self.generator.generate(draft).strip(),
        )

    def test_generates_remove_recipe(self):
        draft = RecipeDraft(kind="remove", item_outputs=[self.item("<minecraft:chest>")], remove_mode="all")
        self.assertEqual("recipes.remove(<minecraft:chest>);", self.generator.generate(draft).strip())

    def test_generates_template_recipe(self):
        draft = RecipeDraft(
            kind="machine",
            template_id="thermal_expansion_furnace",
            item_inputs=[self.item("<minecraft:sand>")],
            item_outputs=[self.item("<minecraft:glass>")],
            eut=4000,
        )
        self.assertEqual(
            "mods.thermalexpansion.Furnace.addRecipe(4000, <minecraft:sand>, <minecraft:glass>);",
            self.generator.generate(draft).strip(),
        )

    def test_generates_generic_gt_machine_recipe(self):
        draft = RecipeDraft(
            kind="machine",
            template_id="generic_gt_machine",
            item_inputs=[self.item("<minecraft:iron_ingot>")],
            item_outputs=[self.item("<minecraft:bucket>")],
            fluid_inputs=[ScriptFluid("water", 1000)],
            fluid_outputs=[],
            duration=200,
            eut=30,
        )
        script = self.generator.generate(draft)
        self.assertIn("mods.gregtech.GenericMachine.addRecipe", script)
        self.assertIn("<liquid:water> * 1000", script)
        self.assertIn("200", script)
        self.assertIn("30", script)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify failure**

Run: `python -m unittest tests.test_zs_generator -v`

Expected: FAIL because model/generator files do not exist.

- [ ] **Step 3: Implement models**

`core/recipe_model.py`:

```python
"""Recipe draft models for ZS generation."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class ScriptItem:
    expression: str
    amount: int = 1
    comment_name: str = ""

    def to_zs(self) -> str:
        base = self.expression.strip()
        if self.amount and self.amount > 1:
            return f"{base} * {self.amount}"
        return base


@dataclass(frozen=True)
class ScriptFluid:
    name_or_expression: str
    amount: int

    def to_zs(self) -> str:
        value = self.name_or_expression.strip()
        if value.startswith("<"):
            base = value
        else:
            base = f"<liquid:{value}>"
        return f"{base} * {self.amount}"


@dataclass
class RecipeDraft:
    kind: str
    item_inputs: List[Optional[ScriptItem]] = field(default_factory=list)
    item_outputs: List[Optional[ScriptItem]] = field(default_factory=list)
    fluid_inputs: List[ScriptFluid] = field(default_factory=list)
    fluid_outputs: List[ScriptFluid] = field(default_factory=list)
    duration: int = 200
    eut: int = 30
    xp: float = 0.0
    remove_mode: str = "all"
    template_id: str = "generic_gt_machine"
```

- [ ] **Step 4: Implement templates**

`core/templates.py`:

```python
"""Built-in machine templates inspired by ModTweaker logger output."""
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class MachineTemplate:
    template_id: str
    display_name: str
    max_item_inputs: int
    max_item_outputs: int
    max_fluid_inputs: int
    max_fluid_outputs: int
    style: str


TEMPLATES: Dict[str, MachineTemplate] = {
    "generic_gt_machine": MachineTemplate("generic_gt_machine", "Generic GT Machine", 16, 4, 4, 4, "generic_gt"),
    "assembler_like": MachineTemplate("assembler_like", "Assembler-like", 16, 4, 4, 4, "generic_gt"),
    "cutter_like": MachineTemplate("cutter_like", "Cutter-like", 16, 4, 4, 4, "generic_gt"),
    "macerator_like": MachineTemplate("macerator_like", "Macerator-like", 16, 4, 4, 4, "generic_gt"),
    "mixer_like": MachineTemplate("mixer_like", "Mixer-like", 16, 4, 4, 4, "generic_gt"),
    "chemical_reactor_like": MachineTemplate("chemical_reactor_like", "Chemical Reactor-like", 16, 4, 4, 4, "generic_gt"),
    "blast_furnace_like": MachineTemplate("blast_furnace_like", "Blast Furnace-like", 16, 4, 4, 4, "generic_gt"),
    "thermal_expansion_furnace": MachineTemplate("thermal_expansion_furnace", "Thermal Expansion Furnace", 1, 1, 0, 0, "te_furnace"),
    "thermal_expansion_pulverizer": MachineTemplate("thermal_expansion_pulverizer", "Thermal Expansion Pulverizer", 1, 2, 0, 0, "te_pulverizer"),
    "appeng_grinder": MachineTemplate("appeng_grinder", "AE Grinder", 1, 3, 0, 0, "ae_grinder"),
    "appeng_inscriber": MachineTemplate("appeng_inscriber", "AE Inscriber", 3, 1, 0, 0, "ae_inscriber"),
}


def template_options() -> List[MachineTemplate]:
    return list(TEMPLATES.values())
```

- [ ] **Step 5: Implement generator**

`core/zs_generator.py`:

```python
"""Generate CraftTweaker and ModTweaker ZS scripts."""
from typing import Iterable, Optional

from core.recipe_model import RecipeDraft, ScriptFluid, ScriptItem
from core.templates import TEMPLATES


class ZsGenerator:
    def generate(self, draft: RecipeDraft) -> str:
        if draft.kind == "shaped":
            return self._shaped(draft)
        if draft.kind == "shapeless":
            return self._shapeless(draft)
        if draft.kind == "furnace":
            return self._furnace(draft)
        if draft.kind == "remove":
            return self._remove(draft)
        if draft.kind == "machine":
            return self._machine(draft)
        raise ValueError(f"Unsupported recipe kind: {draft.kind}")

    def _first_output(self, draft: RecipeDraft) -> ScriptItem:
        for output in draft.item_outputs:
            if output is not None and output.expression.strip():
                return output
        raise ValueError("Output item is required")

    def _non_empty_items(self, items: Iterable[Optional[ScriptItem]]) -> list[ScriptItem]:
        return [item for item in items if item is not None and item.expression.strip()]

    def _item_or_null(self, item: Optional[ScriptItem]) -> str:
        if item is None or not item.expression.strip():
            return "null"
        return item.to_zs()

    def _fluid_list(self, fluids: Iterable[ScriptFluid]) -> str:
        return "[" + ", ".join(fluid.to_zs() for fluid in fluids) + "]"

    def _item_list(self, items: Iterable[Optional[ScriptItem]]) -> str:
        return "[" + ", ".join(item.to_zs() for item in self._non_empty_items(items)) + "]"

    def _shaped(self, draft: RecipeDraft) -> str:
        output = self._first_output(draft).to_zs()
        cells = list(draft.item_inputs[:9])
        while len(cells) < 9:
            cells.append(None)
        rows = []
        for row in range(3):
            row_cells = cells[row * 3:(row + 1) * 3]
            rows.append("  [" + ", ".join(self._item_or_null(cell) for cell in row_cells) + "]")
        return "recipes.addShaped(" + output + ", [\n" + ",\n".join(rows) + "\n]);"

    def _shapeless(self, draft: RecipeDraft) -> str:
        output = self._first_output(draft).to_zs()
        return f"recipes.addShapeless({output}, {self._item_list(draft.item_inputs)});"

    def _furnace(self, draft: RecipeDraft) -> str:
        output = self._first_output(draft).to_zs()
        inputs = self._non_empty_items(draft.item_inputs)
        if not inputs:
            raise ValueError("Furnace input is required")
        return f"furnace.addRecipe({output}, {inputs[0].to_zs()}, {float(draft.xp):.1f});"

    def _remove(self, draft: RecipeDraft) -> str:
        output = self._first_output(draft).to_zs()
        if draft.remove_mode == "shaped":
            return f"recipes.removeShaped({output});"
        if draft.remove_mode == "shapeless":
            return f"recipes.removeShapeless({output});"
        if draft.remove_mode == "furnace":
            return f"furnace.remove({output});"
        return f"recipes.remove({output});"

    def _machine(self, draft: RecipeDraft) -> str:
        template = TEMPLATES.get(draft.template_id)
        if template is None:
            raise ValueError(f"Unknown machine template: {draft.template_id}")
        if template.style == "te_furnace":
            inputs = self._non_empty_items(draft.item_inputs)
            output = self._first_output(draft)
            if not inputs:
                raise ValueError("Machine input is required")
            return f"mods.thermalexpansion.Furnace.addRecipe({draft.eut}, {inputs[0].to_zs()}, {output.to_zs()});"
        if template.style == "te_pulverizer":
            inputs = self._non_empty_items(draft.item_inputs)
            outputs = self._non_empty_items(draft.item_outputs)
            if not inputs or not outputs:
                raise ValueError("Machine input and output are required")
            if len(outputs) > 1:
                return (
                    f"mods.thermalexpansion.Pulverizer.addRecipe({draft.eut}, {inputs[0].to_zs()}, "
                    f"{outputs[0].to_zs()}, {outputs[1].to_zs()}, 100);"
                )
            return f"mods.thermalexpansion.Pulverizer.addRecipe({draft.eut}, {inputs[0].to_zs()}, {outputs[0].to_zs()});"
        if template.style == "ae_grinder":
            inputs = self._non_empty_items(draft.item_inputs)
            outputs = self._non_empty_items(draft.item_outputs)
            if not inputs or not outputs:
                raise ValueError("Machine input and output are required")
            optional1 = outputs[1].to_zs() if len(outputs) > 1 else "null"
            optional2 = outputs[2].to_zs() if len(outputs) > 2 else "null"
            return (
                f"mods.appeng.Grinder.addRecipe({inputs[0].to_zs()}, {outputs[0].to_zs()}, {draft.eut}, "
                f"{optional1}, 0, {optional2}, 0);"
            )
        if template.style == "ae_inscriber":
            inputs = self._non_empty_items(draft.item_inputs)
            output = self._first_output(draft)
            middle = inputs[0].to_zs() if inputs else "null"
            top = inputs[1].to_zs() if len(inputs) > 1 else "null"
            bottom = inputs[2].to_zs() if len(inputs) > 2 else "null"
            return f"mods.appeng.Inscriber.addRecipe([{middle}], {top}, {bottom}, {output.to_zs()}, \"PRESS\");"
        return self._generic_gt(draft)

    def _generic_gt(self, draft: RecipeDraft) -> str:
        return (
            "// GTNH machine template: " + draft.template_id + "\n"
            "// 请根据当前 GTNH/ModTweaker 环境校准目标机器入口。\n"
            "mods.gregtech.GenericMachine.addRecipe(\n"
            f"    {self._item_list(draft.item_inputs)},\n"
            f"    {self._item_list(draft.item_outputs)},\n"
            f"    {self._fluid_list(draft.fluid_inputs)},\n"
            f"    {self._fluid_list(draft.fluid_outputs)},\n"
            f"    {int(draft.duration)},\n"
            f"    {int(draft.eut)}\n"
            ");"
        )
```

- [ ] **Step 6: Run generator tests**

Run: `python -m unittest tests.test_zs_generator -v`

Expected: PASS all 6 tests.

- [ ] **Step 7: Run all tests and commit**

Run: `python -m unittest discover -v`

Expected: PASS all tests.

Commit:

```bash
git add core/recipe_model.py core/templates.py core/zs_generator.py tests/test_zs_generator.py
git commit -m "feat: generate crafttweaker scripts"
```

---

### Task 4: Script Project and Config Persistence

**Files:**
- Create: `core/script_project.py`
- Modify: `utils/helpers.py`
- Test: `tests/test_script_project.py`

- [ ] **Step 1: Write failing tests**

`tests/test_script_project.py`:

```python
import tempfile
import unittest
from pathlib import Path

from core.script_project import AppConfig, save_script


class ScriptProjectTest(unittest.TestCase):
    def test_app_config_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            config = AppConfig(item_index_path="index.json", script_output_dir="scripts")
            config.save(path)
            loaded = AppConfig.load(path)
            self.assertEqual("index.json", loaded.item_index_path)
            self.assertEqual("scripts", loaded.script_output_dir)

    def test_save_script_creates_parent_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "scripts" / "generated.zs"
            save_script(target, "recipes.remove(<minecraft:dirt>);")
            self.assertEqual("recipes.remove(<minecraft:dirt>);", target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify failure**

Run: `python -m unittest tests.test_script_project -v`

Expected: FAIL because `core.script_project` does not exist.

- [ ] **Step 3: Implement script project helpers**

`core/script_project.py`:

```python
"""Configuration and script persistence."""
from dataclasses import asdict, dataclass
from pathlib import Path

from utils.helpers import load_json, save_json


@dataclass
class AppConfig:
    item_index_path: str = "D:/Code/gtnh_item_doc_exporter/item_index.json"
    gtnh_client_path: str = ""
    script_output_dir: str = ""
    window_geometry: str = "1200x820"
    last_template: str = "generic_gt_machine"

    @classmethod
    def load(cls, path: str | Path) -> "AppConfig":
        target = Path(path)
        if not target.exists():
            return cls()
        data = load_json(target)
        return cls(
            item_index_path=str(data.get("item_index_path", cls.item_index_path)),
            gtnh_client_path=str(data.get("gtnh_client_path", "")),
            script_output_dir=str(data.get("script_output_dir", "")),
            window_geometry=str(data.get("window_geometry", "1200x820")),
            last_template=str(data.get("last_template", "generic_gt_machine")),
        )

    def save(self, path: str | Path) -> None:
        save_json(path, asdict(self))


def save_script(path: str | Path, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
```

- [ ] **Step 4: Run tests**

Run: `python -m unittest tests.test_script_project -v`

Expected: PASS all 2 tests.

- [ ] **Step 5: Commit**

```bash
git add core/script_project.py tests/test_script_project.py
git commit -m "feat: persist script builder config"
```

---

### Task 5: Reusable Tkinter Widgets

**Files:**
- Create: `gui/widgets.py`

- [ ] **Step 1: Implement item table and slot widgets**

`gui/widgets.py`:

```python
"""Reusable Tkinter widgets for the script builder."""
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional

from core.item_index import ItemEntry
from core.recipe_model import ScriptFluid, ScriptItem


class ItemSearchFrame(ttk.Frame):
    def __init__(self, parent, on_query: Callable[[str], None], on_pick: Callable[[ItemEntry], None]):
        super().__init__(parent)
        self.on_query = on_query
        self.on_pick = on_pick
        self.entries: List[ItemEntry] = []
        self.query_var = tk.StringVar()
        self.query_var.trace_add("write", lambda *_: self.on_query(self.query_var.get()))
        self._create_widgets()

    def _create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X)
        ttk.Label(top, text="搜索物品:").pack(side=tk.LEFT)
        ttk.Entry(top, textvariable=self.query_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        columns = ("chinese", "english", "ct", "id", "meta", "block")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=18)
        headings = {
            "chinese": "中文名",
            "english": "英文名",
            "ct": "CT 表达式",
            "id": "ID",
            "meta": "meta",
            "block": "方块",
        }
        widths = {"chinese": 120, "english": 140, "ct": 220, "id": 180, "meta": 60, "block": 50}
        for key in columns:
            self.tree.heading(key, text=headings[key])
            self.tree.column(key, width=widths[key], anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-Button-1>", self._on_double_click)

    def set_entries(self, entries: List[ItemEntry]):
        self.entries = entries
        self.tree.delete(*self.tree.get_children())
        for index, entry in enumerate(entries):
            self.tree.insert("", tk.END, iid=str(index), values=(
                entry.chinese_name,
                entry.english_name,
                entry.ct_expression,
                entry.registry_id,
                entry.meta,
                "是" if entry.is_block else "否",
            ))

    def _on_double_click(self, _event):
        item_id = self.tree.focus()
        if item_id:
            self.on_pick(self.entries[int(item_id)])


class SlotButton(ttk.Button):
    def __init__(self, parent, label: str, on_select: Callable[["SlotButton"], None]):
        super().__init__(parent, text=label, command=lambda: on_select(self), width=18)
        self.item: Optional[ScriptItem] = None
        self.default_label = label

    def set_item(self, item: Optional[ScriptItem]):
        self.item = item
        if item is None:
            self.configure(text=self.default_label)
        else:
            self.configure(text=item.to_zs())

    def clear(self):
        self.set_item(None)


class SlotGridFrame(ttk.LabelFrame):
    def __init__(self, parent, text: str, count: int, columns: int, on_select: Callable[[SlotButton], None]):
        super().__init__(parent, text=text, padding=5)
        self.slots: List[SlotButton] = []
        for index in range(count):
            slot = SlotButton(self, f"{index + 1}", on_select)
            slot.grid(row=index // columns, column=index % columns, padx=2, pady=2, sticky=tk.EW)
            self.slots.append(slot)

    def items(self) -> List[Optional[ScriptItem]]:
        return [slot.item for slot in self.slots]


class PreviewFrame(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="ZS 预览", padding=5)
        self.text = tk.Text(self, wrap=tk.NONE, height=24, font=("Consolas", 10))
        self.text.pack(fill=tk.BOTH, expand=True)

    def set_text(self, value: str):
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, value)

    def get_text(self) -> str:
        return self.text.get("1.0", tk.END).rstrip()


class FluidListFrame(ttk.LabelFrame):
    def __init__(self, parent, text: str):
        super().__init__(parent, text=text, padding=5)
        self.name_var = tk.StringVar()
        self.amount_var = tk.StringVar(value="1000")
        row = ttk.Frame(self)
        row.pack(fill=tk.X)
        ttk.Entry(row, textvariable=self.name_var, width=18).pack(side=tk.LEFT, padx=2)
        ttk.Entry(row, textvariable=self.amount_var, width=8).pack(side=tk.LEFT, padx=2)

    def fluids(self) -> List[ScriptFluid]:
        name = self.name_var.get().strip()
        if not name:
            return []
        return [ScriptFluid(name, int(self.amount_var.get() or "0"))]
```

- [ ] **Step 2: Commit**

```bash
git add gui/widgets.py
git commit -m "feat: add script builder widgets"
```

---

### Task 6: Main Window Integration

**Files:**
- Modify: `gui/main_window.py`
- Create: `gui/dialogs.py`

- [ ] **Step 1: Implement dialogs**

`gui/dialogs.py`:

```python
"""Dialog helpers."""
from tkinter import filedialog, messagebox


def choose_item_index(parent, initial: str = "") -> str:
    return filedialog.askopenfilename(
        parent=parent,
        title="选择 item_index.json",
        initialfile=initial,
        filetypes=[("Item index", "item_index.json"), ("JSON", "*.json"), ("All files", "*.*")],
    )


def choose_script_file(parent, initial_dir: str = "") -> str:
    return filedialog.asksaveasfilename(
        parent=parent,
        title="保存 ZS 脚本",
        initialdir=initial_dir,
        defaultextension=".zs",
        filetypes=[("CraftTweaker script", "*.zs"), ("All files", "*.*")],
    )


def show_error(title: str, message: str) -> None:
    messagebox.showerror(title, message)


def show_info(title: str, message: str) -> None:
    messagebox.showinfo(title, message)
```

- [ ] **Step 2: Replace GUI stub with full main window**

`gui/main_window.py`:

```python
"""Main window for GTNH Item Doc Script Builder."""
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from core.item_index import ItemEntry, ItemIndexStore
from core.recipe_model import RecipeDraft, ScriptItem
from core.script_project import AppConfig, save_script
from core.templates import template_options
from core.zs_generator import ZsGenerator
from gui.dialogs import choose_item_index, choose_script_file, show_error, show_info
from gui.widgets import FluidListFrame, ItemSearchFrame, PreviewFrame, SlotButton, SlotGridFrame


class MainWindow:
    TITLE = "GTNH 脚本生成器"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(self.TITLE)
        self.config_path = Path(__file__).resolve().parent.parent / "config.json"
        self.config = AppConfig.load(self.config_path)
        self.root.geometry(self.config.window_geometry)
        self.root.minsize(1000, 680)
        self.store: ItemIndexStore | None = None
        self.generator = ZsGenerator()
        self.selected_slot: SlotButton | None = None
        self.recipe_kind = tk.StringVar(value="shaped")
        self.template_id = tk.StringVar(value=self.config.last_template)
        self.xp_var = tk.StringVar(value="0.0")
        self.duration_var = tk.StringVar(value="200")
        self.eut_var = tk.StringVar(value="30")
        self.remove_mode = tk.StringVar(value="all")
        self.status_var = tk.StringVar(value="准备加载物品索引")
        self._create_widgets()
        self._try_load_default_index()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _create_widgets(self):
        main = ttk.Frame(self.root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)
        toolbar = ttk.Frame(main)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text="选择 item_index.json", command=self._choose_index).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="刷新预览", command=self._refresh_preview).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="保存 .zs", command=self._save_script).pack(side=tk.LEFT, padx=4)
        ttk.Label(toolbar, textvariable=self.status_var).pack(side=tk.RIGHT)

        panes = ttk.PanedWindow(main, orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=True, pady=6)

        self.search_frame = ItemSearchFrame(panes, self._search, self._pick_item)
        panes.add(self.search_frame, weight=2)

        self.editor = ttk.Frame(panes)
        panes.add(self.editor, weight=2)
        self._create_editor(self.editor)

        self.preview = PreviewFrame(panes)
        panes.add(self.preview, weight=2)

    def _create_editor(self, parent):
        mode = ttk.LabelFrame(parent, text="脚本类型", padding=5)
        mode.pack(fill=tk.X)
        for text, value in [("有序合成", "shaped"), ("无序合成", "shapeless"), ("熔炉", "furnace"), ("删除", "remove"), ("GTNH/模组机器", "machine")]:
            ttk.Radiobutton(mode, text=text, variable=self.recipe_kind, value=value, command=self._refresh_preview).pack(side=tk.LEFT)

        self.input_grid = SlotGridFrame(parent, "输入格", 16, 4, self._select_slot)
        self.input_grid.pack(fill=tk.X, pady=4)
        self.output_grid = SlotGridFrame(parent, "输出格", 4, 4, self._select_slot)
        self.output_grid.pack(fill=tk.X, pady=4)

        params = ttk.LabelFrame(parent, text="参数", padding=5)
        params.pack(fill=tk.X)
        ttk.Label(params, text="模板:").grid(row=0, column=0, sticky=tk.W)
        combo = ttk.Combobox(params, textvariable=self.template_id, values=[t.template_id for t in template_options()], state="readonly", width=26)
        combo.grid(row=0, column=1, sticky=tk.W)
        combo.bind("<<ComboboxSelected>>", lambda _e: self._refresh_preview())
        ttk.Label(params, text="XP:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(params, textvariable=self.xp_var, width=10).grid(row=1, column=1, sticky=tk.W)
        ttk.Label(params, text="duration:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(params, textvariable=self.duration_var, width=10).grid(row=2, column=1, sticky=tk.W)
        ttk.Label(params, text="EU/t:").grid(row=3, column=0, sticky=tk.W)
        ttk.Entry(params, textvariable=self.eut_var, width=10).grid(row=3, column=1, sticky=tk.W)
        ttk.Label(params, text="删除模式:").grid(row=4, column=0, sticky=tk.W)
        ttk.Combobox(params, textvariable=self.remove_mode, values=["all", "shaped", "shapeless", "furnace"], state="readonly", width=12).grid(row=4, column=1, sticky=tk.W)

        self.fluid_inputs = FluidListFrame(parent, "流体输入")
        self.fluid_inputs.pack(fill=tk.X, pady=4)
        self.fluid_outputs = FluidListFrame(parent, "流体输出")
        self.fluid_outputs.pack(fill=tk.X, pady=4)

    def _choose_index(self):
        path = choose_item_index(self.root, self.config.item_index_path)
        if path:
            self._load_index(path)

    def _try_load_default_index(self):
        if self.config.item_index_path and Path(self.config.item_index_path).exists():
            self._load_index(self.config.item_index_path)

    def _load_index(self, path: str):
        try:
            self.store = ItemIndexStore.load(path)
            self.config.item_index_path = path
            self.search_frame.set_entries(self.store.search("", limit=500))
            self.status_var.set(f"已加载 {self.store.entry_count} 条，语言 {self.store.language}")
        except Exception as exc:
            show_error("加载失败", str(exc))

    def _search(self, query: str):
        if self.store is None:
            return
        results = self.store.search(query, limit=500)
        self.search_frame.set_entries(results)
        self.status_var.set(f"显示 {len(results)} / {self.store.entry_count} 条")

    def _select_slot(self, slot: SlotButton):
        self.selected_slot = slot

    def _pick_item(self, entry: ItemEntry):
        if self.selected_slot is None:
            self.status_var.set("请先点击一个配方格")
            return
        self.selected_slot.set_item(ScriptItem(entry.ct_expression, 1, entry.chinese_name))
        self._refresh_preview()

    def _draft(self) -> RecipeDraft:
        return RecipeDraft(
            kind=self.recipe_kind.get(),
            item_inputs=self.input_grid.items(),
            item_outputs=self.output_grid.items(),
            fluid_inputs=self.fluid_inputs.fluids(),
            fluid_outputs=self.fluid_outputs.fluids(),
            duration=int(self.duration_var.get() or "0"),
            eut=int(self.eut_var.get() or "0"),
            xp=float(self.xp_var.get() or "0"),
            remove_mode=self.remove_mode.get(),
            template_id=self.template_id.get(),
        )

    def _refresh_preview(self):
        try:
            self.preview.set_text(self.generator.generate(self._draft()))
        except Exception as exc:
            self.preview.set_text(f"// 无法生成脚本: {exc}")

    def _save_script(self):
        self._refresh_preview()
        path = choose_script_file(self.root, self.config.script_output_dir)
        if not path:
            return
        try:
            save_script(path, self.preview.get_text())
            self.config.script_output_dir = str(Path(path).parent)
            show_info("保存成功", path)
        except Exception as exc:
            show_error("保存失败", str(exc))

    def _on_close(self):
        self.config.window_geometry = self.root.geometry()
        self.config.last_template = self.template_id.get()
        self.config.save(self.config_path)
        self.root.destroy()
```

- [ ] **Step 3: Run import smoke test**

Run: `python -c "from gui.main_window import MainWindow; print(MainWindow.TITLE)"`

Expected output includes `GTNH 脚本生成器`.

- [ ] **Step 4: Commit**

```bash
git add gui/main_window.py gui/dialogs.py
git commit -m "feat: wire script builder gui"
```

---

### Task 7: Verification and Packaging

**Files:**
- Modify: `README.md`
- Optional generated: `dist/GTNHItemDocScriptBuilder.exe`

- [ ] **Step 1: Add README**

`README.md`:

````markdown
# GTNHItemDocScriptBuilder

Tkinter desktop tool for generating CraftTweaker / ModTweaker `.zs` scripts from `GTNHItemDocExporter` item indexes.

## Run

```powershell
python main.py
```

## Input

Load `item_index.json`, for example:

```text
D:\Code\gtnh_item_doc_exporter\item_index.json
```

## Supported Script Types

- Shaped crafting
- Shapeless crafting
- Furnace recipe
- Recipe removal
- Template-driven GTNH / ModTweaker machine recipes

## Build

```powershell
.\build.bat
```
````

- [ ] **Step 2: Run full test suite**

Run: `python -m unittest discover -v`

Expected: all tests pass.

- [ ] **Step 3: Run GUI import check**

Run: `python -c "from core.item_index import ItemIndexStore; s=ItemIndexStore.load(r'D:\Code\gtnh_item_doc_exporter\item_index.json'); print(s.entry_count)"`

Expected: prints `57232` when the exported file exists.

- [ ] **Step 4: Build executable when PyInstaller is available**

Run: `python -m PyInstaller build.spec`

Expected: `dist/GTNHItemDocScriptBuilder.exe` exists. If PyInstaller is not installed, install from `requirements.txt` or document that source run is verified and exe packaging remains pending.

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: add script builder usage"
```

---

## Implementation Notes

- Keep GUI text Chinese-first, matching the user's workflow.
- Do not block first release on perfect English names. Current `item_index.json` has many `item.*` / `tile.*` fallback names, so display CT expression and registry ID prominently.
- GTNH/GregTech CraftTweaker support varies by installed addons. Generic GT templates must include a warning comment and remain editable by changing templates later.
- ModTweaker-confirmed templates should use the same argument order shown by its logger classes.
- Never generate a script silently when required output/input is missing; preview should show an explanatory `// 无法生成脚本: ...` message.
