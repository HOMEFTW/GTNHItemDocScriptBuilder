"""Full-screen ZenScript editor window with line numbers, find/replace, and syntax highlighting."""
import tkinter as tk
from tkinter import ttk
from typing import Callable

from gui.syntax_highlight import ZsSyntaxHighlighter


class ScriptEditorWindow(tk.Toplevel):
    """A large editor window for comfortable ZS script editing."""

    SYNC_DEBOUNCE_MS = 300

    def __init__(self, parent, content: str, on_save: Callable[[str], None],
                 on_change: Callable[[str], None] | None = None,
                 on_close: Callable[[], None] | None = None,
                 icon_path=None):
        super().__init__(parent)
        self.on_save = on_save
        self.on_change = on_change
        self.on_close = on_close
        self._sync_id: str | None = None
        self.title("ZS 脚本编辑器")
        self.geometry(parent.winfo_toplevel().geometry())
        self.minsize(800, 600)
        if icon_path:
            try:
                self.iconbitmap(str(icon_path))
            except tk.TclError:
                pass
        self._create_widgets()
        self._bind_shortcuts()
        self.editor.insert("1.0", content)
        self.editor.edit_reset()
        self.editor.edit_modified(False)
        self._highlighter.highlight()
        self._update_line_numbers()
        self.editor.focus_set()
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.transient(parent)
        self.grab_set()

    def _create_widgets(self):
        # Toolbar
        toolbar = ttk.Frame(self, padding=(8, 4))
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text="保存并关闭", command=self._save_and_close).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="撤销", command=self._undo).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="重做", command=self._redo).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="查找", command=self._show_find).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="替换", command=self._show_replace).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="关闭", command=self._close).pack(side=tk.RIGHT, padx=2)

        # Editor area
        editor_frame = ttk.Frame(self)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))

        # Line numbers
        self.line_numbers = tk.Text(
            editor_frame, width=5, padx=4, pady=4,
            background="#f3f4f6", foreground="#6b7280",
            font=("Consolas", 11), state=tk.DISABLED,
            borderwidth=0, highlightthickness=0,
            takefocus=False, cursor="arrow",
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Main editor with scrollbars
        text_container = ttk.Frame(editor_frame)
        text_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.editor = tk.Text(
            text_container, wrap=tk.NONE,
            font=("Consolas", 11), background="#ffffff",
            foreground="#111111", insertbackground="#111111",
            undo=True, maxundo=-1, padx=4, pady=4,
        )
        self._v_scroll = ttk.Scrollbar(text_container, orient=tk.VERTICAL, command=self._on_scroll_y)
        h_scroll = ttk.Scrollbar(text_container, orient=tk.HORIZONTAL, command=self.editor.xview)
        self.editor.configure(yscrollcommand=self._on_editor_yscroll, xscrollcommand=h_scroll.set)
        self.editor.grid(row=0, column=0, sticky=tk.NSEW)
        self._v_scroll.grid(row=0, column=1, sticky=tk.NS)
        h_scroll.grid(row=1, column=0, sticky=tk.EW)
        text_container.rowconfigure(0, weight=1)
        text_container.columnconfigure(0, weight=1)

        # Syntax highlighting
        self._highlighter = ZsSyntaxHighlighter(self.editor, live=True)

        # Search highlight tag
        self.editor.tag_configure("search_highlight", background="#fde68a")
        self.editor.tag_configure("search_current", background="#f59e0b")

        # Line number sync
        self.editor.bind("<<Modified>>", self._on_modified, add="+")
        self.editor.bind("<Configure>", lambda _: self._update_line_numbers())
        self.editor.bind("<KeyRelease>", self._on_key_release)
        self.editor.bind("<MouseWheel>", lambda _: self.after(10, self._sync_line_scroll))
        self.line_numbers.bind("<MouseWheel>", self._redirect_mousewheel)

        # Find/Replace bar (hidden by default)
        self._find_frame = ttk.Frame(self, padding=(8, 4))
        self._find_var = tk.StringVar()
        self._replace_var = tk.StringVar()
        self._find_var.trace_add("write", lambda *_: self._highlight_matches())

        find_row = ttk.Frame(self._find_frame)
        find_row.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(find_row, text="查找:").pack(side=tk.LEFT)
        self._find_entry = ttk.Entry(find_row, textvariable=self._find_var, width=30)
        self._find_entry.pack(side=tk.LEFT, padx=4)
        ttk.Button(find_row, text="上一个", command=self._find_prev).pack(side=tk.LEFT, padx=2)
        ttk.Button(find_row, text="下一个", command=self._find_next).pack(side=tk.LEFT, padx=2)
        self._match_count_label = ttk.Label(find_row, text="")
        self._match_count_label.pack(side=tk.LEFT, padx=8)
        ttk.Button(find_row, text="关闭", command=self._hide_find).pack(side=tk.RIGHT, padx=2)

        self._replace_row = ttk.Frame(self._find_frame)
        ttk.Label(self._replace_row, text="替换:").pack(side=tk.LEFT)
        self._replace_entry = ttk.Entry(self._replace_row, textvariable=self._replace_var, width=30)
        self._replace_entry.pack(side=tk.LEFT, padx=4)
        ttk.Button(self._replace_row, text="替换", command=self._replace_current).pack(side=tk.LEFT, padx=2)
        ttk.Button(self._replace_row, text="全部替换", command=self._replace_all).pack(side=tk.LEFT, padx=2)

        self._find_visible = False
        self._replace_visible = False
        self._line_update_id: str | None = None

    def _bind_shortcuts(self):
        self.bind("<Control-s>", lambda _: self._save_and_close())
        self.bind("<Control-f>", lambda _: self._show_find())
        self.bind("<Control-h>", lambda _: self._show_replace())
        self.bind("<Control-z>", lambda _: self._undo())
        self.bind("<Control-y>", lambda _: self._redo())
        self.bind("<Escape>", self._on_escape)
        self.editor.bind("<Control-a>", self._select_all)

    def _select_all(self, _event):
        self.editor.tag_add(tk.SEL, "1.0", tk.END)
        return "break"

    def _on_escape(self, _event):
        if self._find_visible:
            self._hide_find()
        else:
            self._close()

    def _save_and_close(self):
        content = self.editor.get("1.0", tk.END).rstrip()
        self.on_save(content)
        self.destroy()

    def _close(self):
        if self.on_close:
            self.on_close()
        self.destroy()

    def _schedule_sync(self):
        if self.on_change is None:
            return
        if self._sync_id is not None:
            self.after_cancel(self._sync_id)
        self._sync_id = self.after(self.SYNC_DEBOUNCE_MS, self._do_sync)

    def _do_sync(self):
        self._sync_id = None
        if self.on_change:
            content = self.editor.get("1.0", tk.END).rstrip()
            cursor_line = int(self.editor.index(tk.INSERT).split(".")[0])
            self.on_change(content, cursor_line)

    def _undo(self):
        try:
            self.editor.edit_undo()
        except tk.TclError:
            pass
        return "break"

    def _redo(self):
        try:
            self.editor.edit_redo()
        except tk.TclError:
            pass
        return "break"

    def _on_scroll_y(self, *args):
        self.editor.yview(*args)
        self.line_numbers.yview(*args)

    def _on_editor_yscroll(self, first, last):
        self._v_scroll.set(first, last)
        self.line_numbers.yview_moveto(first)

    def _on_modified(self, _event):
        if self.editor.edit_modified():
            self.editor.edit_modified(False)
            self._schedule_line_update()
            self._schedule_sync()

    def _on_key_release(self, _event):
        self._schedule_line_update()
        self._schedule_sync()

    def _schedule_line_update(self):
        if self._line_update_id is not None:
            self.after_cancel(self._line_update_id)
        self._line_update_id = self.after(50, self._update_line_numbers)

    def _update_line_numbers(self):
        self._line_update_id = None
        self.line_numbers.configure(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        line_count = int(self.editor.index("end-1c").split(".")[0])
        lines = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert("1.0", lines)
        self.line_numbers.configure(state=tk.DISABLED)
        self._sync_line_scroll()

    def _sync_line_scroll(self):
        self.line_numbers.yview_moveto(self.editor.yview()[0])

    def _redirect_mousewheel(self, event):
        self.editor.yview_scroll(-1 * (event.delta // 120), "units")
        self._sync_line_scroll()
        return "break"

    # --- Find / Replace ---

    def _show_find(self):
        if not self._find_visible:
            self._find_frame.pack(fill=tk.X, before=None, side=tk.BOTTOM)
            self._find_visible = True
        if self._replace_visible:
            self._replace_row.pack_forget()
            self._replace_visible = False
        self._find_entry.focus_set()
        sel = self._get_selection()
        if sel:
            self._find_var.set(sel)
        return "break"

    def _show_replace(self):
        if not self._find_visible:
            self._find_frame.pack(fill=tk.X, side=tk.BOTTOM)
            self._find_visible = True
        if not self._replace_visible:
            self._replace_row.pack(fill=tk.X, pady=(2, 0))
            self._replace_visible = True
        self._find_entry.focus_set()
        sel = self._get_selection()
        if sel:
            self._find_var.set(sel)
        return "break"

    def _hide_find(self):
        self._find_frame.pack_forget()
        if self._replace_visible:
            self._replace_row.pack_forget()
        self._find_visible = False
        self._replace_visible = False
        self.editor.tag_remove("search_highlight", "1.0", tk.END)
        self.editor.tag_remove("search_current", "1.0", tk.END)
        self._match_count_label.configure(text="")
        self.editor.focus_set()

    def _get_selection(self) -> str:
        try:
            return self.editor.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            return ""

    def _highlight_matches(self):
        self.editor.tag_remove("search_highlight", "1.0", tk.END)
        self.editor.tag_remove("search_current", "1.0", tk.END)
        query = self._find_var.get()
        if not query:
            self._match_count_label.configure(text="")
            return
        count = 0
        start = "1.0"
        while True:
            pos = self.editor.search(query, start, stopindex=tk.END, nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(query)}c"
            self.editor.tag_add("search_highlight", pos, end)
            start = end
            count += 1
        self._match_count_label.configure(text=f"{count} 个匹配")

    def _find_next(self):
        query = self._find_var.get()
        if not query:
            return
        start = self.editor.index(tk.INSERT)
        pos = self.editor.search(query, f"{start}+1c", stopindex=tk.END, nocase=True)
        if not pos:
            pos = self.editor.search(query, "1.0", stopindex=start, nocase=True)
        if pos:
            self._select_match(pos, query)

    def _find_prev(self):
        query = self._find_var.get()
        if not query:
            return
        start = self.editor.index(tk.INSERT)
        pos = self.editor.search(query, start, stopindex="1.0", backwards=True, nocase=True)
        if not pos:
            pos = self.editor.search(query, tk.END, stopindex=start, backwards=True, nocase=True)
        if pos:
            self._select_match(pos, query)

    def _select_match(self, pos: str, query: str):
        end = f"{pos}+{len(query)}c"
        self.editor.tag_remove("search_current", "1.0", tk.END)
        self.editor.tag_add("search_current", pos, end)
        self.editor.mark_set(tk.INSERT, pos)
        self.editor.see(pos)

    def _replace_current(self):
        query = self._find_var.get()
        replacement = self._replace_var.get()
        if not query:
            return
        try:
            sel_start = self.editor.index("search_current.first")
            sel_end = self.editor.index("search_current.last")
            self.editor.delete(sel_start, sel_end)
            self.editor.insert(sel_start, replacement)
            self._highlight_matches()
            self._find_next()
        except tk.TclError:
            self._find_next()

    def _replace_all(self):
        query = self._find_var.get()
        replacement = self._replace_var.get()
        if not query:
            return
        content = self.editor.get("1.0", tk.END)
        new_content = content.replace(query, replacement)
        if new_content != content:
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", new_content.rstrip("\n"))
            self._highlight_matches()
