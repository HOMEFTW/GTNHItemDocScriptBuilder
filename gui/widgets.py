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
        self.output_chance = 10000
        self.default_label = label

    def set_item(self, item: Optional[ScriptItem]):
        self.item = item
        if item is None:
            self.configure(text=self.default_label)
        else:
            self.configure(text=item.to_zs())

    def clear(self):
        self.set_item(None)
        self.output_chance = 10000


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
        self.full_file_frame, self.full_text, self.full_vertical_scrollbar, self.full_horizontal_scrollbar = (
            self._create_text_panel("完整 .zs 文件（未导入）")
        )
        self.generated_frame, self.generated_text, self.generated_vertical_scrollbar, self.generated_horizontal_scrollbar = (
            self._create_text_panel("保存内容 / 当前草稿")
        )
        self.full_file_frame.grid(row=0, column=0, sticky=tk.NSEW, pady=(0, 3))
        self.generated_frame.grid(row=1, column=0, sticky=tk.NSEW, pady=(3, 0))
        self.rowconfigure(0, weight=1, uniform="preview")
        self.rowconfigure(1, weight=1, uniform="preview")
        self.columnconfigure(0, weight=1)
        self.text = self.generated_text
        self.vertical_scrollbar = self.generated_vertical_scrollbar
        self.horizontal_scrollbar = self.generated_horizontal_scrollbar

    def _create_text_panel(self, title: str):
        frame = ttk.LabelFrame(self, text=title, padding=5)
        text = tk.Text(
            frame,
            wrap=tk.NONE,
            height=10,
            font=("Consolas", 10),
            background="#ffffff",
            foreground="#111111",
            insertbackground="#111111",
            undo=True,
            maxundo=-1,
        )
        vertical_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        horizontal_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=text.xview)
        text.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )
        text.grid(row=0, column=0, sticky=tk.NSEW)
        vertical_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        horizontal_scrollbar.grid(row=1, column=0, sticky=tk.EW)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        return frame, text, vertical_scrollbar, horizontal_scrollbar

    def set_full_text(self, value: str):
        self.full_text.delete("1.0", tk.END)
        self.full_text.insert(tk.END, value)
        self.full_text.edit_reset()

    def get_full_text(self) -> str:
        return self.full_text.get("1.0", tk.END).rstrip()

    def set_full_label(self, label: str):
        self.full_file_frame.configure(text=f"完整 .zs 文件: {label}")

    def set_source_label(self, label: str):
        self.generated_frame.configure(text=f"保存内容 / {label}")

    def set_text(self, value: str):
        self.generated_text.delete("1.0", tk.END)
        self.generated_text.insert(tk.END, value)

    def get_text(self) -> str:
        return self.generated_text.get("1.0", tk.END).rstrip()


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
        self.comment_name = ""
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
        self.comment_name = entry.chinese_name

    def set_fluids(self, fluids: List[ScriptFluid]):
        if not fluids:
            self.clear()
            return
        self.name_var.set(fluids[0].name_or_expression)
        self.amount_var.set(str(fluids[0].amount))
        self.comment_name = fluids[0].comment_name

    def clear(self):
        self.name_var.set("")
        self.comment_name = ""

    def fluids(self) -> List[ScriptFluid]:
        name = self.name_var.get().strip()
        if not name:
            return []
        return [ScriptFluid(name, int(self.amount_var.get() or "0"), getattr(self, "comment_name", ""))]


class FluidRowFrame(ttk.Frame):
    def __init__(
        self,
        parent,
        index: int,
        on_search: Callable[["FluidRowFrame"], None],
        on_change: Callable[[], None],
    ):
        super().__init__(parent)
        self.on_search = on_search
        self.on_change = on_change
        self.name_var = tk.StringVar()
        self.amount_var = tk.StringVar(value="1000")
        self.comment_name = ""
        self.name_var.trace_add("write", lambda *_: self.on_change())
        self.amount_var.trace_add("write", lambda *_: self.on_change())
        self.grid_label = ttk.Label(self, text=f"{index + 1}:")
        self.grid_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 2), pady=2)
        self.fluid_entry = ttk.Entry(self, textvariable=self.name_var)
        self.fluid_entry.grid(row=0, column=1, sticky=tk.EW, padx=2, pady=2)
        ttk.Label(self, text="数量:").grid(row=0, column=2, sticky=tk.W, padx=(4, 2), pady=2)
        self.amount_entry = ttk.Entry(self, textvariable=self.amount_var, width=8)
        self.amount_entry.grid(row=0, column=3, sticky=tk.W, padx=2, pady=2)
        self.search_button = ttk.Button(self, text="搜索", command=lambda: self.on_search(self))
        self.search_button.grid(row=0, column=4, sticky=tk.W, padx=2, pady=2)
        ttk.Button(self, text="清空", command=self.clear).grid(row=0, column=5, sticky=tk.W, padx=2, pady=2)
        self.columnconfigure(1, weight=1)

    def set_search_enabled(self, enabled: bool):
        self.search_button.configure(state=tk.NORMAL if enabled else tk.DISABLED)

    def set_fluid(self, entry: FluidEntry):
        self.name_var.set(entry.ct_expression)
        self.comment_name = entry.chinese_name

    def clear(self):
        self.name_var.set("")
        self.comment_name = ""

    def fluid(self) -> Optional[ScriptFluid]:
        name = self.name_var.get().strip()
        if not name:
            return None
        return ScriptFluid(name, int(self.amount_var.get() or "0"), self.comment_name)


class FluidListRowsFrame(ttk.LabelFrame):
    def __init__(
        self,
        parent,
        text: str,
        count: int,
        on_search: Callable[[FluidRowFrame], None],
        on_change: Callable[[], None],
        adjustable: bool = False,
    ):
        super().__init__(parent, text=text, padding=5)
        self.on_search = on_search
        self.on_change = on_change
        self.adjustable = adjustable
        self.count_var = tk.StringVar(value=str(max(count, 1)))
        if adjustable:
            controls = ttk.Frame(self)
            controls.pack(fill=tk.X, pady=(0, 3))
            self.count_label_widget = ttk.Label(controls, text="条数:")
            self.count_label_widget.pack(side=tk.LEFT)
            self.count_entry = ttk.Entry(controls, textvariable=self.count_var, width=5)
            self.count_entry.pack(side=tk.LEFT, padx=(4, 8))
            self.count_var.trace_add("write", lambda *_: self._sync_row_count_from_var())
        self.row_container = ttk.Frame(self)
        self.row_container.pack(fill=tk.X)
        self.rows: List[FluidRowFrame] = []
        self._set_row_count(max(count, 1))

    def set_search_enabled(self, enabled: bool):
        for row in self.rows:
            row.set_search_enabled(enabled)

    def set_fluids(self, fluids: List[ScriptFluid]):
        if self.adjustable:
            self.count_var.set(str(max(len(fluids), 1)))
        for row, fluid in zip(self.rows, fluids):
            row.name_var.set(fluid.name_or_expression)
            row.amount_var.set(str(fluid.amount))
            row.comment_name = fluid.comment_name
        for row in self.rows[len(fluids) :]:
            row.clear()

    def fluids(self) -> List[ScriptFluid]:
        return [fluid for row in self.rows if (fluid := row.fluid()) is not None]

    def _sync_row_count_from_var(self):
        value = self.count_var.get().strip()
        if not value:
            return
        try:
            count = int(value)
        except ValueError:
            return
        self._set_row_count(max(count, 1))

    def _set_row_count(self, count: int):
        while len(self.rows) > count:
            row = self.rows.pop()
            row.destroy()
        while len(self.rows) < count:
            row = FluidRowFrame(self.row_container, len(self.rows), self.on_search, self.on_change)
            row.pack(fill=tk.X, pady=1)
            self.rows.append(row)
