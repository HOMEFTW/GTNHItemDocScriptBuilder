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
        top.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(top, text="搜索物品:").pack(side=tk.LEFT)
        ttk.Entry(top, textvariable=self.query_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        columns = ("chinese", "english", "ct", "id", "meta", "block")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=18)
        headings = {
            "chinese": "中文名",
            "english": "英文名",
            "ct": "CT 表达式",
            "id": "游戏 ID",
            "meta": "Meta",
            "block": "方块",
        }
        widths = {"chinese": 120, "english": 140, "ct": 220, "id": 180, "meta": 64, "block": 52}
        for key in columns:
            self.tree.heading(key, text=headings[key])
            self.tree.column(key, width=widths[key], anchor=tk.W)

        scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<Double-Button-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._copy_focused_expression)

    def set_entries(self, entries: List[ItemEntry]):
        self.entries = entries
        self.tree.delete(*self.tree.get_children())
        for index, entry in enumerate(entries):
            self.tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    entry.chinese_name,
                    entry.english_name,
                    entry.ct_expression,
                    entry.registry_id,
                    entry.meta,
                    "是" if entry.is_block else "否",
                ),
            )

    def _on_double_click(self, _event):
        item_id = self.tree.focus()
        if item_id:
            self.on_pick(self.entries[int(item_id)])

    def _copy_focused_expression(self, _event):
        item_id = self.tree.focus()
        if item_id:
            self.clipboard_clear()
            self.clipboard_append(self.entries[int(item_id)].ct_expression)


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
            self.columnconfigure(index % columns, weight=1)
            self.slots.append(slot)

    def items(self) -> List[Optional[ScriptItem]]:
        return [slot.item for slot in self.slots]

    def clear(self):
        for slot in self.slots:
            slot.clear()


class PreviewFrame(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="ZS 预览", padding=5)
        self.text = tk.Text(
            self,
            wrap=tk.NONE,
            height=24,
            font=("Consolas", 10),
            background="#ffffff",
            foreground="#111111",
            insertbackground="#111111",
        )
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
        ttk.Label(row, text="流体:").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.name_var, width=18).pack(side=tk.LEFT, padx=2)
        ttk.Label(row, text="数量:").pack(side=tk.LEFT, padx=(8, 0))
        ttk.Entry(row, textvariable=self.amount_var, width=8).pack(side=tk.LEFT, padx=2)

    def fluids(self) -> List[ScriptFluid]:
        name = self.name_var.get().strip()
        if not name:
            return []
        return [ScriptFluid(name, int(self.amount_var.get() or "0"))]
