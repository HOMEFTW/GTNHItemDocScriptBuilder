"""Reusable Tkinter widgets for the script builder."""
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional

from core.fluid_index import FluidEntry, FluidIndexStore
from core.item_index import ItemEntry
from core.ore_dictionary_index import OreDictionaryEntry, OreDictionaryIndexStore
from core.recipe_model import ScriptFluid, ScriptItem
from gui.debounce import DebouncedCallback
from gui.syntax_highlight import ZsSyntaxHighlighter
from gui.tooltip import ToolTip


class ItemSearchFrame(ttk.Frame):
    def __init__(self, parent, on_query: Callable[[str], None], on_pick: Callable[[ItemEntry], None]):
        super().__init__(parent)
        self.on_query = on_query
        self.on_pick = on_pick
        self.entries: List[ItemEntry] = []
        self.query_var = tk.StringVar()
        self._debounced_query = DebouncedCallback(self, 180, lambda: self.on_query(self.query_var.get()))
        self.query_var.trace_add("write", lambda *_: self._debounced_query())
        self._create_widgets()

    def _create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(top, text="搜索物品:").pack(side=tk.LEFT)
        ttk.Entry(top, textvariable=self.query_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.filter_var = tk.StringVar(value="全部")
        self.filter_combo = ttk.Combobox(
            top,
            textvariable=self.filter_var,
            values=("全部", "只搜物品", "只搜方块"),
            state="readonly",
            width=8,
        )
        self.filter_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.filter_combo.bind("<<ComboboxSelected>>", lambda _: self._debounced_query())

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
        self.tree.bind("<Button-3>", self._show_context_menu)

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

    def _show_context_menu(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        self.tree.selection_set(item_id)
        self.tree.focus(item_id)
        entry = self.entries[int(item_id)]
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="填入选中格", command=lambda: self.on_pick(entry))
        menu.add_separator()
        menu.add_command(label="复制 CT 表达式", command=lambda: self._copy_to_clipboard(entry.ct_expression))
        menu.add_command(label="复制 Registry ID", command=lambda: self._copy_to_clipboard(entry.registry_id))
        if entry.chinese_name:
            menu.add_command(label="复制中文名", command=lambda: self._copy_to_clipboard(entry.chinese_name))
        menu.post(event.x_root, event.y_root)

    def _copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)

    @property
    def filter_type(self) -> str:
        mapping = {"全部": "all", "只搜物品": "item", "只搜方块": "block"}
        return mapping.get(self.filter_var.get(), "all")


class SlotButton(ttk.Button):
    def __init__(self, parent, label: str, on_select: Callable[["SlotButton"], None]):
        super().__init__(parent, text=label, command=lambda: on_select(self), width=12)
        self.item: Optional[ScriptItem] = None
        self.output_chance = 10000
        self.default_label = label
        self._tooltip = ToolTip(self, f"配方格 {label}")
        self.bind("<Button-3>", self._show_context_menu)

    def set_item(self, item: Optional[ScriptItem]):
        self.item = item
        if item is None:
            self.configure(text=self.default_label)
            self._tooltip.update_text(f"配方格 {self.default_label}")
        else:
            self.configure(text=item.to_zs())
            tip = item.comment_name or item.expression
            if item.amount != 1:
                tip += f" * {item.amount}"
            self._tooltip.update_text(tip)
        self.update_visual_state(False)

    def clear(self):
        self.set_item(None)
        self.output_chance = 10000

    def update_visual_state(self, is_selected: bool):
        if is_selected:
            self.configure(style="Selected.TButton")
        elif self.item is not None and self.output_chance < 10000:
            self.configure(style="ChanceReduced.TButton")
        elif self.item is not None:
            self.configure(style="Filled.TButton")
        else:
            self.configure(style="TButton")

    def _show_context_menu(self, event):
        menu = tk.Menu(self, tearoff=0)
        if self.item is not None:
            menu.add_command(label="复制表达式", command=lambda: self._copy_to_clipboard(self.item.to_zs()))
            menu.add_separator()
        menu.add_command(label="清空此格", command=self.clear)
        menu.post(event.x_root, event.y_root)

    def _copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)


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
    def __init__(self, parent, generated_parent=None):
        super().__init__(parent, text="ZenScript", padding=5)
        self.full_file_frame, self.full_text, self.full_vertical_scrollbar, self.full_horizontal_scrollbar = (
            self._create_text_panel("完整 .zs 文件（未导入）")
        )
        self.generated_frame, self.generated_text, self.generated_vertical_scrollbar, self.generated_horizontal_scrollbar = (
            self._create_text_panel("生成预览 · 尚未写入脚本", parent=generated_parent)
        )
        self.full_file_frame.grid(row=0, column=0, sticky=tk.NSEW, pady=(0, 3))
        self.expand_button = ttk.Button(self.full_file_frame, text="全屏", command=self._open_editor, width=4)
        self.expand_button.place(relx=1.0, y=0, anchor=tk.NE)
        if generated_parent is None:
            self.generated_frame.grid(row=1, column=0, sticky=tk.NSEW, pady=(3, 0))
            self.rowconfigure(1, weight=1)
        self.rowconfigure(0, weight=3)
        self.columnconfigure(0, weight=1)
        self.text = self.generated_text
        self.vertical_scrollbar = self.generated_vertical_scrollbar
        self.horizontal_scrollbar = self.generated_horizontal_scrollbar
        self._full_highlighter = ZsSyntaxHighlighter(self.full_text, live=True)
        self._generated_highlighter = ZsSyntaxHighlighter(self.generated_text)
        self._icon_path = None
        self.save_document = None
        self._create_find_bar()
        self.line_numbers = tk.Canvas(self.full_file_frame, width=46, background="#eef2f6", highlightthickness=0)
        self.full_text.grid_configure(column=1)
        self.full_vertical_scrollbar.grid_configure(column=2)
        self.full_horizontal_scrollbar.grid_configure(column=1)
        self.full_file_frame.columnconfigure(0, weight=0)
        self.full_file_frame.columnconfigure(1, weight=1)
        self.line_numbers.grid(row=0, column=0, sticky=tk.NS)
        self.full_text.configure(yscrollcommand=self._on_editor_scroll)
        self.full_text.bind("<<Modified>>", lambda _e: self._draw_line_numbers(), add="+")
        self.full_text.bind("<Configure>", lambda _e: self._draw_line_numbers(), add="+")

    def _on_editor_scroll(self, first, last):
        self.full_vertical_scrollbar.set(first, last)
        self._draw_line_numbers()

    def _draw_line_numbers(self):
        if not self.winfo_exists():
            return
        self.line_numbers.delete("all")
        index = self.full_text.index("@0,0")
        while True:
            info = self.full_text.dlineinfo(index)
            if info is None:
                break
            self.line_numbers.create_text(36, info[1], anchor="ne", text=index.split(".")[0],
                                          fill="#718096", font=("Consolas", 10))
            index = self.full_text.index(f"{index}+1line")

    def _create_find_bar(self):
        self.find_bar = ttk.Frame(self, padding=4)
        self.find_var = tk.StringVar()
        ttk.Label(self.find_bar, text="查找").pack(side=tk.LEFT)
        self.find_entry = ttk.Entry(self.find_bar, textvariable=self.find_var, width=30)
        self.find_entry.pack(side=tk.LEFT, padx=6)
        self.find_entry.bind("<Return>", lambda _e: self.find_next())
        self.find_entry.bind("<Escape>", lambda _e: self.hide_find())
        ttk.Button(self.find_bar, text="下一个", command=self.find_next).pack(side=tk.LEFT)
        ttk.Button(self.find_bar, text="关闭", command=self.hide_find).pack(side=tk.RIGHT)
        self.find_result = ttk.Label(self.find_bar, text="")
        self.find_result.pack(side=tk.LEFT, padx=8)

    def show_find(self):
        self.find_bar.grid(row=2, column=0, sticky=tk.EW)
        self.find_entry.focus_set()
        return "break"

    def hide_find(self):
        self.find_bar.grid_remove()
        self.full_text.tag_remove("find_match", "1.0", tk.END)
        self.full_text.focus_set()
        return "break"

    def find_next(self):
        query = self.find_var.get()
        self.full_text.tag_remove("find_match", "1.0", tk.END)
        if not query:
            self.find_result.configure(text="请输入查找内容")
            return
        pos = self.full_text.search(query, tk.INSERT, stopindex=tk.END, nocase=True)
        if not pos:
            pos = self.full_text.search(query, "1.0", stopindex=tk.END, nocase=True)
        self.find_result.configure(text="" if pos else "未找到")
        if pos:
            end = f"{pos}+{len(query)}c"
            self.full_text.tag_configure("find_match", background="#fde68a")
            self.full_text.tag_add("find_match", pos, end)
            self.full_text.mark_set(tk.INSERT, end)
            self.full_text.see(pos)

    def set_icon_path(self, path):
        self._icon_path = path

    def _open_editor(self):
        from gui.script_editor import ScriptEditorWindow
        content = self.get_full_text()
        self._lock_full_text()
        self._editor_window = ScriptEditorWindow(
            self.winfo_toplevel(), content,
            on_save=self._on_editor_save,
            on_change=self._on_editor_change,
            on_close=self._on_editor_close,
            icon_path=self._icon_path,
        )

    def _lock_full_text(self):
        self._full_text_locked = True
        self.full_text.bind("<Key>", self._block_input)

    def _unlock_full_text(self):
        self._full_text_locked = False
        self.full_text.unbind("<Key>")

    def _block_input(self, _event):
        return "break"

    def _on_editor_save(self, content: str):
        self._on_editor_change(content)
        if self.save_document is not None:
            return self.save_document()
        return True

    def _on_editor_change(self, content: str, cursor_line: int = 1):
        self.full_text.delete("1.0", tk.END)
        self.full_text.insert(tk.END, content)
        self._full_highlighter.highlight()
        self.full_text.see(f"{cursor_line}.0")

    def _on_editor_close(self):
        self._unlock_full_text()
        self._editor_window = None

    def _create_text_panel(self, title: str, parent=None):
        frame = ttk.LabelFrame(parent if parent is not None else self, text=title, padding=5)
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
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            pady=8,
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
        text.bind("<Button-3>", lambda e: self._show_text_context_menu(e, text))
        return frame, text, vertical_scrollbar, horizontal_scrollbar

    def _show_text_context_menu(self, event, text_widget: tk.Text):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="复制选中", command=lambda: self._copy_selection(text_widget))
        menu.add_command(label="复制全部", command=lambda: self._copy_all(text_widget))
        menu.add_separator()
        menu.add_command(label="全选", command=lambda: text_widget.tag_add(tk.SEL, "1.0", tk.END))
        menu.post(event.x_root, event.y_root)

    def _copy_selection(self, text_widget: tk.Text):
        try:
            selected = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected)
        except tk.TclError:
            pass

    def _copy_all(self, text_widget: tk.Text):
        content = text_widget.get("1.0", tk.END).rstrip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)

    def set_full_text(self, value: str):
        self.full_text.delete("1.0", tk.END)
        self.full_text.insert(tk.END, value)
        self.full_text.edit_reset()
        self._full_highlighter.highlight()

    def get_full_text(self) -> str:
        return self.full_text.get("1.0", "end-1c")

    def set_full_label(self, label: str):
        self.full_file_frame.configure(text=f"完整 .zs 文件: {label}")

    def set_source_label(self, label: str):
        self.generated_frame.configure(text=f"生成预览 / {label}")

    def set_text(self, value: str):
        self.generated_text.configure(state=tk.NORMAL)
        self.generated_text.delete("1.0", tk.END)
        self.generated_text.insert(tk.END, value)
        self._generated_highlighter.highlight()
        self.generated_text.configure(state=tk.DISABLED)

    def get_text(self) -> str:
        return self.generated_text.get("1.0", tk.END).rstrip()


class FluidSearchDialog(tk.Toplevel):
    def __init__(self, parent, store: FluidIndexStore, on_pick: Callable[[FluidEntry], None]):
        super().__init__(parent)
        self.store = store
        self.on_pick = on_pick
        self.entries: List[FluidEntry] = []
        self.query_var = tk.StringVar()
        self._debounced_search = DebouncedCallback(self, 180, self._search)
        self.query_var.trace_add("write", lambda *_: self._debounced_search())
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
        self._debounced_search = DebouncedCallback(self, 180, self._search)
        self.query_var.trace_add("write", lambda *_: self._debounced_search())
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
