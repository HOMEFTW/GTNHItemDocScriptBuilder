"""Main window for GTNH Item Doc Script Builder."""
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from core.item_index import ItemEntry, ItemIndexStore
from core.recipe_model import RecipeDraft, ScriptItem
from core.script_project import AppConfig, save_script
from core.templates import TEMPLATES, recipe_map_options, template_options
from core.zs_generator import ZsGenerator
from gui.dialogs import choose_item_index, choose_script_file, show_error, show_info
from gui.widgets import FluidListFrame, ItemSearchFrame, PreviewFrame, SlotButton, SlotGridFrame


class MainWindow:
    TITLE = "GTNH 脚本生成器"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(self.TITLE)
        self._configure_style()
        self.config_path = Path(__file__).resolve().parent.parent / "config.json"
        self.config = AppConfig.load(self.config_path)
        self.root.geometry(self.config.window_geometry)
        self.root.minsize(1000, 680)
        self.store: ItemIndexStore | None = None
        self.generator = ZsGenerator()
        self.selected_slot: SlotButton | None = None
        self.recipe_kind = tk.StringVar(value="shaped")
        self.template_id = tk.StringVar(value=self.config.last_template)
        self.recipe_map = tk.StringVar(value=self.config.last_recipe_map or self._default_recipe_map(self.config.last_template))
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

    def _configure_style(self):
        self.root.configure(background="#f3f4f6")
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", background="#f3f4f6", foreground="#111111")
        style.configure("TFrame", background="#f3f4f6")
        style.configure("TLabelframe", background="#f3f4f6", foreground="#111111")
        style.configure("TLabelframe.Label", background="#f3f4f6", foreground="#111111")
        style.configure("Treeview", background="#ffffff", foreground="#111111", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", background="#e5e7eb", foreground="#111111")

    def _create_widgets(self):
        main = ttk.Frame(self.root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        toolbar = ttk.Frame(main)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text="选择 item_index.json", command=self._choose_index).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="刷新预览", command=self._refresh_preview).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="复制预览", command=self._copy_preview).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="保存 .zs", command=self._save_script).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="清空格子", command=self._clear_slots).pack(side=tk.LEFT, padx=4)
        ttk.Label(toolbar, textvariable=self.status_var).pack(side=tk.RIGHT)

        panes = ttk.PanedWindow(main, orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=True, pady=6)

        self.search_frame = ItemSearchFrame(panes, self._search, self._pick_item)
        panes.add(self.search_frame, weight=2)

        editor = ttk.Frame(panes)
        panes.add(editor, weight=2)
        self._create_editor(editor)

        self.preview = PreviewFrame(panes)
        panes.add(self.preview, weight=2)
        self._refresh_preview()

    def _create_editor(self, parent):
        mode = ttk.LabelFrame(parent, text="脚本类型", padding=5)
        mode.pack(fill=tk.X)
        modes = [
            ("有序合成", "shaped"),
            ("无序合成", "shapeless"),
            ("熔炉", "furnace"),
            ("删除", "remove"),
            ("GTNH/模组机器", "machine"),
        ]
        for text, value in modes:
            ttk.Radiobutton(mode, text=text, variable=self.recipe_kind, value=value, command=self._refresh_preview).pack(
                side=tk.LEFT,
                padx=(0, 8),
            )

        self.input_grid = SlotGridFrame(parent, "输入格 16 格（有序合成使用前 9 格）", 16, 4, self._select_slot)
        self.input_grid.pack(fill=tk.X, pady=4)
        self.output_grid = SlotGridFrame(parent, "输出格 4 格（普通配方使用第 1 格）", 4, 4, self._select_slot)
        self.output_grid.pack(fill=tk.X, pady=4)

        params = ttk.LabelFrame(parent, text="参数", padding=5)
        params.pack(fill=tk.X)
        ttk.Label(params, text="模板:").grid(row=0, column=0, sticky=tk.W, pady=2)
        combo = ttk.Combobox(
            params,
            textvariable=self.template_id,
            values=[template.template_id for template in template_options()],
            state="readonly",
            width=28,
        )
        combo.grid(row=0, column=1, sticky=tk.W, pady=2)
        combo.bind("<<ComboboxSelected>>", lambda _event: self._on_template_selected())

        ttk.Label(params, text="Recipe Map:").grid(row=1, column=0, sticky=tk.W, pady=2)
        map_combo = ttk.Combobox(
            params,
            textvariable=self.recipe_map,
            values=recipe_map_options(),
            state="readonly",
            width=32,
        )
        map_combo.grid(row=1, column=1, sticky=tk.W, pady=2)
        map_combo.bind("<<ComboboxSelected>>", lambda _event: self._refresh_preview())

        ttk.Label(params, text="XP:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(params, textvariable=self.xp_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        ttk.Label(params, text="Duration:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(params, textvariable=self.duration_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=2)
        ttk.Label(params, text="EU/t:").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Entry(params, textvariable=self.eut_var, width=10).grid(row=4, column=1, sticky=tk.W, pady=2)
        ttk.Label(params, text="删除模式:").grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Combobox(
            params,
            textvariable=self.remove_mode,
            values=["all", "shaped", "shapeless", "furnace", "machine"],
            state="readonly",
            width=12,
        ).grid(row=5, column=1, sticky=tk.W, pady=2)

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
        self.status_var.set(f"已选择配方格 {slot.default_label}，双击左侧物品填入")

    def _on_template_selected(self):
        self.recipe_map.set(self._default_recipe_map(self.template_id.get()))
        self._refresh_preview()

    def _default_recipe_map(self, template_id: str) -> str:
        template = TEMPLATES.get(template_id)
        if template is None:
            return "gt.recipe.assembler"
        return template.recipe_map or "gt.recipe.assembler"

    def _pick_item(self, entry: ItemEntry):
        if self.selected_slot is None:
            self.status_var.set("请先点击一个配方格")
            return
        self.selected_slot.set_item(ScriptItem(entry.ct_expression, 1, entry.chinese_name))
        self.status_var.set(f"已填入 {entry.chinese_name or entry.registry_id}")
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
            recipe_map=self.recipe_map.get(),
        )

    def _refresh_preview(self):
        try:
            self.preview.set_text(self.generator.generate(self._draft()))
        except Exception as exc:
            self.preview.set_text(f"// 无法生成脚本: {exc}")

    def _copy_preview(self):
        text = self.preview.get_text()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set("已复制 ZS 预览")

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

    def _clear_slots(self):
        self.input_grid.clear()
        self.output_grid.clear()
        self.selected_slot = None
        self._refresh_preview()
        self.status_var.set("已清空配方格")

    def _on_close(self):
        self.config.window_geometry = self.root.geometry()
        self.config.last_template = self.template_id.get()
        self.config.last_recipe_map = self.recipe_map.get()
        self.config.save(self.config_path)
        self.root.destroy()
