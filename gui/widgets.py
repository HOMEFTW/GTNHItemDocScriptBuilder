"""Reusable Tkinter widgets for the script builder."""
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional

from core.fluid_index import FluidEntry, FluidIndexStore
from core.item_index import ItemEntry
from core.ore_dictionary_index import OreDictionaryEntry, OreDictionaryIndexStore
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

        table = ttk.Frame(self)
        table.pack(fill=tk.BOTH, expand=True)

        columns = ("chinese", "english", "ct", "id", "meta", "block")
        self.tree = ttk.Treeview(table, columns=columns, show="headings", height=18)
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

        vertical_scrollbar = ttk.Scrollbar(table, orient=tk.VERTICAL, command=self.tree.yview)
        self.horizontal_scrollbar = ttk.Scrollbar(table, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=self.horizontal_scrollbar.set,
        )
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        vertical_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.horizontal_scrollbar.grid(row=1, column=0, sticky=tk.EW)
        table.rowconfigure(0, weight=1)
        table.columnconfigure(0, weight=1)
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
        super().__init__(parent, text=label, command=lambda: on_select(self), width=12)
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
        self.vertical_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.text.yview)
        self.horizontal_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.text.xview)
        self.text.configure(
            yscrollcommand=self.vertical_scrollbar.set,
            xscrollcommand=self.horizontal_scrollbar.set,
        )
        self.text.grid(row=0, column=0, sticky=tk.NSEW)
        self.vertical_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.horizontal_scrollbar.grid(row=1, column=0, sticky=tk.EW)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def set_text(self, value: str):
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, value)

    def get_text(self) -> str:
        return self.text.get("1.0", tk.END).rstrip()


class FluidSearchDialog(tk.Toplevel):
    def __init__(self, parent, store: FluidIndexStore, on_pick: Callable[[FluidEntry], None]):
        super().__init__(parent)
        self.store = store
        self.on_pick = on_pick
        self.entries: List[FluidEntry] = []
        self.query_var = tk.StringVar()
        self.query_var.trace_add("write", lambda *_: self._search())
        self.title("选择流体")
        self.geometry("760x420")
        self.transient(parent)
        self.grab_set()
        self._create_widgets()
        self._search()
        self.query_entry.focus_set()

    def _create_widgets(self):
        root = ttk.Frame(self, padding=8)
        root.pack(fill=tk.BOTH, expand=True)
        top = ttk.Frame(root)
        top.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(top, text="搜索流体:").pack(side=tk.LEFT)
        self.query_entry = ttk.Entry(top, textvariable=self.query_var)
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        columns = ("chinese", "fluid", "ct", "temperature", "gaseous")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=16)
        headings = {
            "chinese": "中文名",
            "fluid": "Fluid Name",
            "ct": "CT 表达式",
            "temperature": "温度",
            "gaseous": "气体",
        }
        widths = {"chinese": 180, "fluid": 190, "ct": 230, "temperature": 60, "gaseous": 52}
        for key in columns:
            self.tree.heading(key, text=headings[key])
            self.tree.column(key, width=widths[key], anchor=tk.W)
        scroll = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<Double-Button-1>", self._on_double_click)
        self.tree.bind("<Return>", self._on_double_click)

    def _search(self):
        self.set_entries(self.store.search(self.query_var.get(), limit=500))

    def set_entries(self, entries: List[FluidEntry]):
        self.entries = entries
        self.tree.delete(*self.tree.get_children())
        for index, entry in enumerate(entries):
            self.tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    entry.chinese_name,
                    entry.fluid_name,
                    entry.ct_expression,
                    entry.temperature,
                    "是" if entry.gaseous else "否",
                ),
            )

    def _on_double_click(self, _event):
        item_id = self.tree.focus()
        if item_id:
            self.on_pick(self.entries[int(item_id)])
            self.destroy()


class OreDictionarySearchDialog(tk.Toplevel):
    def __init__(self, parent, store: OreDictionaryIndexStore, on_pick: Callable[[OreDictionaryEntry], None]):
        super().__init__(parent)
        self.store = store
        self.on_pick = on_pick
        self.entries: List[OreDictionaryEntry] = []
        self.query_var = tk.StringVar()
        self.query_var.trace_add("write", lambda *_: self._search())
        self.title("选择矿物字典")
        self.geometry("860x460")
        self.transient(parent)
        self.grab_set()
        self._create_widgets()
        self._search()
        self.query_entry.focus_set()

    def _create_widgets(self):
        root = ttk.Frame(self, padding=8)
        root.pack(fill=tk.BOTH, expand=True)
        top = ttk.Frame(root)
        top.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(top, text="搜索 OreDict:").pack(side=tk.LEFT)
        self.query_entry = ttk.Entry(top, textvariable=self.query_var)
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        table = ttk.Frame(root)
        table.pack(fill=tk.BOTH, expand=True)
        columns = ("ore", "ct", "count", "items")
        self.tree = ttk.Treeview(table, columns=columns, show="headings", height=16)
        headings = {
            "ore": "OreDict 名称",
            "ct": "CT 表达式",
            "count": "物品数",
            "items": "包含物品",
        }
        widths = {"ore": 180, "ct": 220, "count": 60, "items": 420}
        for key in columns:
            self.tree.heading(key, text=headings[key])
            self.tree.column(key, width=widths[key], anchor=tk.W)
        vertical_scrollbar = ttk.Scrollbar(table, orient=tk.VERTICAL, command=self.tree.yview)
        self.horizontal_scrollbar = ttk.Scrollbar(table, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=self.horizontal_scrollbar.set,
        )
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        vertical_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.horizontal_scrollbar.grid(row=1, column=0, sticky=tk.EW)
        table.rowconfigure(0, weight=1)
        table.columnconfigure(0, weight=1)
        self.tree.bind("<Double-Button-1>", self._on_double_click)
        self.tree.bind("<Return>", self._on_double_click)

    def _search(self):
        self.set_entries(self.store.search(self.query_var.get(), limit=500))

    def set_entries(self, entries: List[OreDictionaryEntry]):
        self.entries = entries
        self.tree.delete(*self.tree.get_children())
        for index, entry in enumerate(entries):
            self.tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    entry.ore_name,
                    entry.ct_expression,
                    entry.item_count,
                    " ".join(entry.items[:12]),
                ),
            )

    def _on_double_click(self, _event):
        item_id = self.tree.focus()
        if item_id:
            self.on_pick(self.entries[int(item_id)])
            self.destroy()


class FluidListFrame(ttk.LabelFrame):
    def __init__(
        self,
        parent,
        text: str,
        on_search: Callable[["FluidListFrame"], None],
        on_change: Callable[[], None],
    ):
        super().__init__(parent, text=text, padding=5)
        self.on_search = on_search
        self.on_change = on_change
        self.name_var = tk.StringVar()
        self.amount_var = tk.StringVar(value="1000")
        self.name_var.trace_add("write", lambda *_: self.on_change())
        self.amount_var.trace_add("write", lambda *_: self.on_change())
        ttk.Label(self, text="流体:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.fluid_entry = ttk.Entry(self, textvariable=self.name_var)
        self.fluid_entry.grid(row=0, column=1, sticky=tk.EW, padx=2, pady=2)
        self.search_button = ttk.Button(self, text="搜索", command=lambda: self.on_search(self))
        self.search_button.grid(row=0, column=2, sticky=tk.W, padx=2, pady=2)
        ttk.Button(self, text="清空", command=self.clear).grid(row=0, column=3, sticky=tk.W, padx=2, pady=2)
        ttk.Label(self, text="数量:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.amount_entry = ttk.Entry(self, textvariable=self.amount_var, width=10)
        self.amount_entry.grid(row=1, column=1, sticky=tk.W, padx=2, pady=2)
        self.columnconfigure(1, weight=1)

    def set_search_enabled(self, enabled: bool):
        self.search_button.configure(state=tk.NORMAL if enabled else tk.DISABLED)

    def set_fluid(self, entry: FluidEntry):
        self.name_var.set(entry.ct_expression)

    def clear(self):
        self.name_var.set("")

    def fluids(self) -> List[ScriptFluid]:
        name = self.name_var.get().strip()
        if not name:
            return []
        return [ScriptFluid(name, int(self.amount_var.get() or "0"))]
