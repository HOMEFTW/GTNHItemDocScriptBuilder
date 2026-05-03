"""Main window for GTNH Item Doc Script Builder."""
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from core.fluid_index import FluidEntry, FluidIndexStore, default_fluid_index_path
from core.item_index import ItemEntry, ItemIndexStore
from core.ore_dictionary_index import (
    OreDictionaryEntry,
    OreDictionaryIndexStore,
    default_ore_dictionary_index_path,
)
from core.recipe_layout import (
    LAYOUTS,
    layout_key_for,
    remove_mode_id_from_label,
    remove_mode_label,
    remove_mode_label_options,
)
from core.recipe_model import RecipeDraft, ScriptFluid, ScriptItem
from core.script_project import AppConfig, save_script
from core.templates import (
    TEMPLATES,
    recipe_map_id_from_label,
    recipe_map_label,
    recipe_map_label_options,
    template_options,
)
from core.zs_generator import ZsGenerator
from core.zs_parser import parse_zs_script
from gui.dialogs import choose_import_script_file, choose_item_index, choose_script_file, show_error, show_info
from gui.widgets import (
    FluidListFrame,
    FluidListRowsFrame,
    FluidSearchDialog,
    ItemSearchFrame,
    OreDictionarySearchDialog,
    PreviewFrame,
    SlotButton,
    SlotGridFrame,
)


MIN_WINDOW_SIZE = (1400, 900)
# UI priority: preserve this three-pane balance before adding new controls.
SEARCH_PANE_WIDTH = 580
PREVIEW_PANE_WIDTH = 400
SEARCH_PANE_WEIGHT = 0
EDITOR_PANE_WEIGHT = 6
PREVIEW_PANE_WEIGHT = 0


class MainWindow:
    TITLE = "GTNH 脚本生成器"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(self.TITLE)
        self._configure_style()
        self.config_path = Path(__file__).resolve().parent.parent / "config.json"
        self.config = AppConfig.load(self.config_path)
        self.root.geometry(self.config.window_geometry)
        self.root.minsize(*MIN_WINDOW_SIZE)
        self.store: ItemIndexStore | None = None
        self.fluid_store: FluidIndexStore | None = None
        self.ore_dictionary_store: OreDictionaryIndexStore | None = None
        self.generator = ZsGenerator()
        self.selected_slot: SlotButton | None = None
        self.active_input_grid: SlotGridFrame | None = None
        self.active_output_grid: SlotGridFrame | None = None
        self.slot_editor_frames: dict[str, ttk.Frame] = {}
        self.slot_editors: dict[str, tuple[SlotGridFrame, SlotGridFrame]] = {}
        self.recipe_kind = tk.StringVar(value="shaped")
        self.template_id = tk.StringVar(value=self.config.last_template)
        initial_recipe_map = self.config.last_recipe_map or self._default_recipe_map(self.config.last_template)
        self.recipe_map = tk.StringVar(value=recipe_map_label(recipe_map_id_from_label(initial_recipe_map)))
        self.xp_var = tk.StringVar(value="0.0")
        self.include_furnace_xp = tk.BooleanVar(value=True)
        self.shaped_mirrored = tk.BooleanVar(value=False)
        self.fuel_ticks_var = tk.StringVar(value="1600")
        self.duration_var = tk.StringVar(value="200")
        self.eut_var = tk.StringVar(value="30")
        self.special_value_var = tk.StringVar(value="")
        self.special_item: ScriptItem | None = None
        self.special_item_var = tk.StringVar(value="")
        self.output_chance_var = tk.StringVar(value="10000")
        self.remove_mode = tk.StringVar(value=remove_mode_label("shaped"))
        self.status_var = tk.StringVar(value="准备加载物品索引")
        self.no_fluid_inputs = tk.BooleanVar(value=False)
        self.no_fluid_outputs = tk.BooleanVar(value=False)
        self.no_fluid_inputs.trace_add("write", lambda *_: self._refresh_preview())
        self.no_fluid_outputs.trace_add("write", lambda *_: self._refresh_preview())
        self.include_furnace_xp.trace_add("write", lambda *_: self._refresh_preview())
        self.shaped_mirrored.trace_add("write", lambda *_: self._refresh_preview())
        self.fuel_ticks_var.trace_add("write", lambda *_: self._refresh_preview())
        self.special_value_var.trace_add("write", lambda *_: self._refresh_preview())
        self.selected_item_amount = tk.StringVar(value="1")
        self.selected_item_suffix = tk.StringVar(value="")
        self._syncing_selected_item_options = False
        self.selected_item_amount.trace_add("write", lambda *_: self._apply_selected_item_options())
        self.selected_item_suffix.trace_add("write", lambda *_: self._apply_selected_item_options())
        self.output_chance_var.trace_add("write", lambda *_: self._apply_selected_output_chance())
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
        ttk.Button(toolbar, text="导入 .zs", command=self._import_script).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="刷新预览", command=self._refresh_preview).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="复制预览", command=self._copy_preview).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="保存 .zs", command=self._save_script).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="清空格子", command=self._clear_slots).pack(side=tk.LEFT, padx=4)
        self.ore_dictionary_button = ttk.Button(toolbar, text="填入 OreDict", command=self._choose_ore_dictionary)
        self.ore_dictionary_button.pack(side=tk.LEFT, padx=4)
        self._set_ore_dictionary_search_enabled(False)
        ttk.Label(toolbar, textvariable=self.status_var).pack(side=tk.RIGHT)

        panes = ttk.PanedWindow(main, orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=True, pady=6)

        self.search_frame = ItemSearchFrame(panes, self._search, self._pick_item)
        self.search_frame.configure(width=SEARCH_PANE_WIDTH)
        self.search_frame.pack_propagate(False)
        panes.add(self.search_frame, weight=SEARCH_PANE_WEIGHT)

        editor = ttk.Frame(panes)
        panes.add(editor, weight=EDITOR_PANE_WEIGHT)
        self._create_scrollable_editor(editor)

        self.preview = PreviewFrame(panes)
        self.preview.configure(width=PREVIEW_PANE_WIDTH)
        self.preview.pack_propagate(False)
        self.preview.grid_propagate(False)
        panes.add(self.preview, weight=PREVIEW_PANE_WEIGHT)
        self._refresh_preview()

    def _create_scrollable_editor(self, parent):
        self.editor_canvas = tk.Canvas(
            parent,
            borderwidth=0,
            highlightthickness=0,
            background="#f3f4f6",
        )
        self.editor_vertical_scrollbar = ttk.Scrollbar(
            parent,
            orient=tk.VERTICAL,
            command=self.editor_canvas.yview,
        )
        self.editor_canvas.configure(yscrollcommand=self.editor_vertical_scrollbar.set)
        self.editor_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.editor_vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.editor_content = ttk.Frame(self.editor_canvas)
        self.editor_window = self.editor_canvas.create_window((0, 0), window=self.editor_content, anchor=tk.NW)
        self.editor_content.bind(
            "<Configure>",
            lambda _event: self.editor_canvas.configure(scrollregion=self.editor_canvas.bbox("all")),
        )
        self.editor_canvas.bind(
            "<Configure>",
            lambda event: self.editor_canvas.itemconfigure(self.editor_window, width=event.width),
        )
        self._create_editor(self.editor_content)

    def _create_editor(self, parent):
        mode = ttk.LabelFrame(parent, text="脚本类型", padding=5)
        mode.pack(fill=tk.X)
        modes = [
            ("有序合成", "shaped"),
            ("无序合成", "shapeless"),
            ("熔炉", "furnace"),
            ("燃料", "fuel"),
            ("删除", "remove"),
            ("GTNH/模组机器", "machine"),
        ]
        for text, value in modes:
            ttk.Radiobutton(
                mode,
                text=text,
                variable=self.recipe_kind,
                value=value,
                command=self._on_recipe_kind_selected,
            ).pack(side=tk.LEFT, padx=(0, 8))

        self.slot_area = ttk.Frame(parent)
        self.slot_area.pack(fill=tk.X, pady=4)
        self._create_slot_editors(self.slot_area)

        item_options = ttk.LabelFrame(parent, text="选中物品格", padding=5)
        item_options.pack(fill=tk.X, pady=4)
        ttk.Label(item_options, text="数量:").grid(row=0, column=0, sticky=tk.W, padx=(0, 4), pady=2)
        ttk.Entry(item_options, textvariable=self.selected_item_amount, width=8).grid(
            row=0,
            column=1,
            sticky=tk.W,
            padx=(0, 8),
            pady=2,
        )
        ttk.Label(item_options, text="后缀:").grid(row=0, column=2, sticky=tk.W, padx=(0, 4), pady=2)
        self.selected_item_suffix_entry = ttk.Entry(item_options, textvariable=self.selected_item_suffix)
        self.selected_item_suffix_entry.grid(row=0, column=3, sticky=tk.EW, pady=2)
        self.output_chance_label_widget = ttk.Label(item_options, text="输出概率:")
        self.output_chance_label_widget.grid(row=1, column=0, sticky=tk.W, padx=(0, 4), pady=2)
        self.output_chance_entry = ttk.Entry(item_options, textvariable=self.output_chance_var, width=10)
        self.output_chance_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 8), pady=2)
        item_options.columnconfigure(3, weight=1)

        params = ttk.LabelFrame(parent, text="参数", padding=5)
        params.pack(fill=tk.X)
        self.template_label_widget = ttk.Label(params, text="模板:")
        self.template_label_widget.grid(row=0, column=0, sticky=tk.W, pady=2)
        self.template_combo = ttk.Combobox(
            params,
            textvariable=self.template_id,
            values=[template.template_id for template in template_options()],
            state="readonly",
            width=28,
        )
        self.template_combo.grid(row=0, column=1, sticky=tk.W, pady=2)
        self.template_combo.bind("<<ComboboxSelected>>", lambda _event: self._on_template_selected())

        self.recipe_map_label_widget = ttk.Label(params, text="Recipe Map:")
        self.recipe_map_label_widget.grid(row=1, column=0, sticky=tk.W, pady=2)
        self.recipe_map_combo = ttk.Combobox(
            params,
            textvariable=self.recipe_map,
            values=recipe_map_label_options(),
            state="readonly",
            width=42,
        )
        self.recipe_map_combo.grid(row=1, column=1, sticky=tk.W, pady=2)
        self.recipe_map_combo.bind("<<ComboboxSelected>>", lambda _event: self._refresh_preview())

        self.xp_label_widget = ttk.Label(params, text="XP:")
        self.xp_label_widget.grid(row=2, column=0, sticky=tk.W, pady=2)
        self.xp_entry = ttk.Entry(params, textvariable=self.xp_var, width=10)
        self.xp_entry.grid(row=2, column=1, sticky=tk.W, pady=2)
        self.include_furnace_xp_checkbox = ttk.Checkbutton(
            params,
            text="写入熔炉 XP",
            variable=self.include_furnace_xp,
        )
        self.include_furnace_xp_checkbox.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=2)
        self.duration_label_widget = ttk.Label(params, text="Duration:")
        self.duration_label_widget.grid(row=3, column=0, sticky=tk.W, pady=2)
        self.duration_entry = ttk.Entry(params, textvariable=self.duration_var, width=10)
        self.duration_entry.grid(row=3, column=1, sticky=tk.W, pady=2)
        self.special_value_label_widget = ttk.Label(params, text="Special Value:")
        self.special_value_label_widget.grid(row=5, column=0, sticky=tk.W, pady=2)
        self.special_value_entry = ttk.Entry(params, textvariable=self.special_value_var, width=10)
        self.special_value_entry.grid(row=5, column=1, sticky=tk.W, pady=2)
        self.special_item_label_widget = ttk.Label(params, text="Special Item:")
        self.special_item_label_widget.grid(row=10, column=0, sticky=tk.W, pady=2)
        self.special_item_entry = ttk.Entry(params, textvariable=self.special_item_var, width=42, state="readonly")
        self.special_item_entry.grid(row=10, column=1, sticky=tk.W, pady=2)
        self.special_item_button = ttk.Button(
            params,
            text="从当前选中物品填入",
            command=self._set_special_item_from_selected_slot,
        )
        self.special_item_button.grid(row=11, column=0, sticky=tk.W, pady=2)
        self.special_item_clear_button = ttk.Button(
            params,
            text="清空 Special Item",
            command=self._clear_special_item,
        )
        self.special_item_clear_button.grid(row=11, column=1, sticky=tk.E, pady=2)
        self.shaped_mirrored_checkbox = ttk.Checkbutton(
            params,
            text="镜像有序合成",
            variable=self.shaped_mirrored,
        )
        self.shaped_mirrored_checkbox.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=2)
        self.eut_label_widget = ttk.Label(params, text="EU/t:")
        self.eut_label_widget.grid(row=4, column=0, sticky=tk.W, pady=2)
        self.eut_entry = ttk.Entry(params, textvariable=self.eut_var, width=10)
        self.eut_entry.grid(row=4, column=1, sticky=tk.W, pady=2)
        self.fuel_ticks_label_widget = ttk.Label(params, text="燃烧时间:")
        self.fuel_ticks_label_widget.grid(row=7, column=0, sticky=tk.W, pady=2)
        self.fuel_ticks_entry = ttk.Entry(params, textvariable=self.fuel_ticks_var, width=10)
        self.fuel_ticks_entry.grid(row=7, column=1, sticky=tk.W, pady=2)
        self.no_fluid_inputs_checkbox = ttk.Checkbutton(
            params,
            text="无流体输入",
            variable=self.no_fluid_inputs,
        )
        self.no_fluid_inputs_checkbox.grid(row=8, column=0, sticky=tk.W, pady=2)
        self.no_fluid_outputs_checkbox = ttk.Checkbutton(
            params,
            text="无流体输出",
            variable=self.no_fluid_outputs,
        )
        self.no_fluid_outputs_checkbox.grid(row=8, column=1, sticky=tk.W, pady=2)
        self.remove_mode_label_widget = ttk.Label(params, text="删除布局:")
        self.remove_mode_label_widget.grid(row=9, column=0, sticky=tk.W, pady=2)
        self.remove_mode_combo = ttk.Combobox(
            params,
            textvariable=self.remove_mode,
            values=remove_mode_label_options(),
            state="readonly",
            width=12,
        )
        self.remove_mode_combo.grid(row=9, column=1, sticky=tk.W, pady=2)
        self.remove_mode_combo.bind("<<ComboboxSelected>>", lambda _event: self._on_remove_mode_selected())

        self.fluid_inputs = FluidListFrame(parent, "流体输入", self._choose_fluid, self._refresh_preview)
        self.fluid_inputs.pack(fill=tk.X, pady=4)
        self.fluid_outputs = FluidListFrame(parent, "流体输出", self._choose_fluid, self._refresh_preview)
        self.fluid_outputs.pack(fill=tk.X, pady=4)
        self.remove_fluid_inputs = FluidListRowsFrame(
            parent,
            "GT 删除流体输入",
            4,
            self._choose_fluid,
            self._refresh_preview,
        )
        self.remove_fluid_inputs.pack(fill=tk.X, pady=4)
        self._set_fluid_search_enabled(False)
        self._show_slot_editor(self.recipe_kind.get())
        self._update_parameter_visibility()

    def _create_slot_editors(self, parent):
        for kind, layout in LAYOUTS.items():
            frame = ttk.Frame(parent)
            input_grid = SlotGridFrame(
                frame,
                layout.input_title,
                layout.input_count,
                layout.input_columns,
                self._select_slot,
            )
            input_grid.pack(fill=tk.X, pady=4)
            output_grid = SlotGridFrame(
                frame,
                layout.output_title,
                layout.output_count,
                layout.output_columns,
                self._select_slot,
            )
            output_grid.pack(fill=tk.X, pady=4)
            self.slot_editor_frames[kind] = frame
            self.slot_editors[kind] = (input_grid, output_grid)

    def _show_slot_editor(self, kind: str):
        for frame in self.slot_editor_frames.values():
            frame.pack_forget()
        layout_key = layout_key_for(kind, self.remove_mode.get())
        frame = self.slot_editor_frames.get(layout_key) or self.slot_editor_frames["shaped"]
        frame.pack(fill=tk.X)
        self.active_input_grid, self.active_output_grid = self.slot_editors.get(layout_key, self.slot_editors["shaped"])
        self.selected_slot = None
        self._sync_selected_item_options()
        self._update_output_chance_visibility()

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
            fluid_status = self._load_fluid_index(path)
            ore_dictionary_status = self._load_ore_dictionary_index(path)
            self.config.item_index_path = path
            self.search_frame.set_entries(self.store.search("", limit=500))
            self.status_var.set(
                f"已加载 {self.store.entry_count} 条物品/方块{fluid_status}{ore_dictionary_status}，语言 {self.store.language}"
            )
        except Exception as exc:
            show_error("加载失败", str(exc))

    def _load_fluid_index(self, item_index_path: str) -> str:
        fluid_path = default_fluid_index_path(item_index_path)
        if not fluid_path.exists():
            self.fluid_store = None
            self._set_fluid_search_enabled(False)
            return "，未找到流体索引"
        try:
            self.fluid_store = FluidIndexStore.load(fluid_path)
            self._set_fluid_search_enabled(True)
            return f"，{self.fluid_store.entry_count} 个流体"
        except Exception as exc:
            self.fluid_store = None
            self._set_fluid_search_enabled(False)
            return f"，流体索引加载失败：{exc}"

    def _load_ore_dictionary_index(self, item_index_path: str) -> str:
        ore_dictionary_path = default_ore_dictionary_index_path(item_index_path)
        if not ore_dictionary_path.exists():
            self.ore_dictionary_store = None
            self._set_ore_dictionary_search_enabled(False)
            return "，未找到矿物字典索引"
        try:
            self.ore_dictionary_store = OreDictionaryIndexStore.load(ore_dictionary_path)
            self._set_ore_dictionary_search_enabled(True)
            return f"，{self.ore_dictionary_store.entry_count} 个矿物字典"
        except Exception as exc:
            self.ore_dictionary_store = None
            self._set_ore_dictionary_search_enabled(False)
            return f"，矿物字典索引加载失败：{exc}"

    def _search(self, query: str):
        if self.store is None:
            return
        results = self.store.search(query, limit=500)
        self.search_frame.set_entries(results)
        self.status_var.set(f"显示 {len(results)} / {self.store.entry_count} 条")

    def _select_slot(self, slot: SlotButton):
        self.selected_slot = slot
        self._sync_selected_item_options()
        self._update_output_chance_visibility()
        self.status_var.set(f"已选择配方格 {slot.default_label}，双击左侧物品填入")

    def _on_recipe_kind_selected(self):
        self._show_slot_editor(self.recipe_kind.get())
        self._update_parameter_visibility()
        self._refresh_preview()

    def _on_remove_mode_selected(self):
        if self.recipe_kind.get() == "remove":
            self._show_slot_editor("remove")
        self._update_parameter_visibility()
        self._refresh_preview()

    def _update_remove_options_visibility(self):
        if self.recipe_kind.get() == "remove":
            self.remove_mode_label_widget.grid()
            self.remove_mode_combo.grid()
        else:
            self.remove_mode_label_widget.grid_remove()
            self.remove_mode_combo.grid_remove()

    def _update_minetweaker_options_visibility(self):
        kind = self.recipe_kind.get()
        if kind == "shaped":
            self.shaped_mirrored_checkbox.grid()
        else:
            self.shaped_mirrored_checkbox.grid_remove()
        if kind == "furnace":
            self.include_furnace_xp_checkbox.grid()
        else:
            self.include_furnace_xp_checkbox.grid_remove()
        if kind == "fuel":
            self.fuel_ticks_label_widget.grid()
            self.fuel_ticks_entry.grid()
        else:
            self.fuel_ticks_label_widget.grid_remove()
            self.fuel_ticks_entry.grid_remove()

    def _update_common_parameter_visibility(self):
        kind = self.recipe_kind.get()
        remove_mode = remove_mode_id_from_label(self.remove_mode.get())
        shows_machine_parameters = kind == "machine" or (kind == "remove" and remove_mode == "machine")
        shows_machine_recipe_parameters = kind == "machine"
        shows_furnace_parameters = kind == "furnace"
        self._set_grid_visible(
            [self.template_label_widget, self.template_combo, self.recipe_map_label_widget, self.recipe_map_combo],
            shows_machine_parameters,
        )
        self._set_grid_visible([self.xp_label_widget, self.xp_entry], shows_furnace_parameters)
        self._set_grid_visible(
            [
                self.duration_label_widget,
                self.duration_entry,
                self.eut_label_widget,
                self.eut_entry,
                self.special_value_label_widget,
                self.special_value_entry,
                self.special_item_label_widget,
                self.special_item_entry,
                self.special_item_button,
                self.special_item_clear_button,
            ],
            shows_machine_recipe_parameters,
        )
        self._set_grid_visible(
            [self.no_fluid_inputs_checkbox, self.no_fluid_outputs_checkbox],
            shows_machine_recipe_parameters,
        )

    def _update_fluid_visibility(self):
        kind = self.recipe_kind.get()
        remove_mode = remove_mode_id_from_label(self.remove_mode.get())
        show_inputs = kind == "machine"
        show_remove_inputs = kind == "remove" and remove_mode == "machine"
        show_outputs = kind == "machine"
        self._set_pack_visible(self.fluid_inputs, show_inputs)
        self._set_pack_visible(self.remove_fluid_inputs, show_remove_inputs)
        self._set_pack_visible(self.fluid_outputs, show_outputs)

    def _update_parameter_visibility(self):
        self._update_remove_options_visibility()
        self._update_minetweaker_options_visibility()
        self._update_common_parameter_visibility()
        self._update_fluid_visibility()

    def _set_grid_visible(self, widgets, visible: bool):
        for widget in widgets:
            if visible:
                widget.grid()
            else:
                widget.grid_remove()

    def _set_pack_visible(self, widget, visible: bool):
        if visible:
            if widget.winfo_manager() != "pack":
                widget.pack(fill=tk.X, pady=4)
        else:
            if widget.winfo_manager() == "pack":
                widget.pack_forget()

    def _on_template_selected(self):
        self.recipe_map.set(recipe_map_label(self._default_recipe_map(self.template_id.get())))
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
        self._sync_selected_item_options()
        self.status_var.set(f"已填入 {entry.chinese_name or entry.registry_id}")
        self._refresh_preview()

    def _choose_ore_dictionary(self):
        if self.ore_dictionary_store is None:
            self.status_var.set("未加载 ore_dictionary_index.json，请选择包含矿物字典索引的 item_index.json")
            return
        if self.selected_slot is None:
            self.status_var.set("请先点击一个配方输入格")
            return
        if self.active_input_grid and self.selected_slot not in self.active_input_grid.slots:
            self.status_var.set("OreDict 只能填入配方输入格")
            return
        OreDictionarySearchDialog(
            self.root,
            self.ore_dictionary_store,
            self._pick_ore_dictionary,
        )

    def _pick_ore_dictionary(self, entry: OreDictionaryEntry):
        if self.selected_slot is None:
            self.status_var.set("请先点击一个配方输入格")
            return
        if self.active_input_grid and self.selected_slot not in self.active_input_grid.slots:
            self.status_var.set("OreDict 只能填入配方输入格")
            return
        self.selected_slot.set_item(ScriptItem(entry.ct_expression, 1, "OreDict " + entry.ore_name))
        self._sync_selected_item_options()
        self.status_var.set(f"已填入 {entry.ct_expression}")
        self._refresh_preview()

    def _sync_selected_item_options(self):
        self._syncing_selected_item_options = True
        try:
            item = self.selected_slot.item if self.selected_slot else None
            self.selected_item_amount.set(str(item.amount if item else 1))
            self.selected_item_suffix.set(item.suffix if item else "")
            chance = self.selected_slot.output_chance if self.selected_slot else 10000
            self.output_chance_var.set(str(chance))
        finally:
            self._syncing_selected_item_options = False

    def _apply_selected_item_options(self):
        if self._syncing_selected_item_options:
            return
        if self.selected_slot is None or self.selected_slot.item is None:
            return
        try:
            amount = int(self.selected_item_amount.get() or "0")
        except ValueError:
            self.status_var.set("物品数量必须是整数")
            return
        item = self.selected_slot.item
        self.selected_slot.set_item(
            ScriptItem(
                item.expression,
                amount,
                item.comment_name,
                self.selected_item_suffix.get(),
            )
        )
        self._refresh_preview()

    def _apply_selected_output_chance(self):
        if self._syncing_selected_item_options:
            return
        if not self._selected_slot_is_machine_output():
            return
        try:
            chance = int(self.output_chance_var.get() or "0")
        except ValueError:
            self.status_var.set("输出概率必须是整数，10000 表示 100%")
            return
        self.selected_slot.output_chance = chance
        self._refresh_preview()

    def _selected_slot_is_machine_output(self) -> bool:
        return (
            self.recipe_kind.get() == "machine"
            and self.selected_slot is not None
            and self.active_output_grid is not None
            and self.selected_slot in self.active_output_grid.slots
        )

    def _update_output_chance_visibility(self):
        if self._selected_slot_is_machine_output():
            self.output_chance_label_widget.grid()
            self.output_chance_entry.grid()
        else:
            self.output_chance_label_widget.grid_remove()
            self.output_chance_entry.grid_remove()

    def _choose_fluid(self, target: FluidListFrame):
        if self.fluid_store is None:
            self.status_var.set("未加载 fluid_index.json，请选择包含流体索引的导出目录中的 item_index.json")
            return
        FluidSearchDialog(self.root, self.fluid_store, lambda entry: self._pick_fluid(target, entry))

    def _pick_fluid(self, target: FluidListFrame, entry: FluidEntry):
        target.set_fluid(entry)
        self.status_var.set(f"已填入流体 {entry.chinese_name or entry.fluid_name}")
        self._refresh_preview()

    def _set_fluid_search_enabled(self, enabled: bool):
        if hasattr(self, "fluid_inputs"):
            self.fluid_inputs.set_search_enabled(enabled)
        if hasattr(self, "fluid_outputs"):
            self.fluid_outputs.set_search_enabled(enabled)
        if hasattr(self, "remove_fluid_inputs"):
            self.remove_fluid_inputs.set_search_enabled(enabled)

    def _set_ore_dictionary_search_enabled(self, enabled: bool):
        if hasattr(self, "ore_dictionary_button"):
            self.ore_dictionary_button.configure(state=tk.NORMAL if enabled else tk.DISABLED)

    def _draft(self) -> RecipeDraft:
        input_grid = self.active_input_grid or self.slot_editors["shaped"][0]
        output_grid = self.active_output_grid or self.slot_editors["shaped"][1]
        kind = self.recipe_kind.get()
        remove_mode = remove_mode_id_from_label(self.remove_mode.get())
        fluid_inputs = self.remove_fluid_inputs.fluids() if kind == "remove" and remove_mode == "machine" else self.fluid_inputs.fluids()
        return RecipeDraft(
            kind=kind,
            item_inputs=input_grid.items(),
            item_outputs=output_grid.items(),
            output_chances=self._output_chances(output_grid),
            fluid_inputs=fluid_inputs,
            fluid_outputs=self.fluid_outputs.fluids(),
            duration=int(self.duration_var.get() or "0"),
            eut=int(self.eut_var.get() or "0"),
            special_value=self._special_value(),
            special_item=self.special_item if self.recipe_kind.get() == "machine" else None,
            xp=float(self.xp_var.get() or "0"),
            include_furnace_xp=bool(self.include_furnace_xp.get()),
            shaped_mirrored=bool(self.shaped_mirrored.get()),
            fuel_ticks=int(self.fuel_ticks_var.get() or "0"),
            remove_mode=remove_mode_id_from_label(self.remove_mode.get()),
            template_id=self.template_id.get(),
            recipe_map=recipe_map_id_from_label(self.recipe_map.get()),
            no_fluid_inputs=bool(self.no_fluid_inputs.get()),
            no_fluid_outputs=bool(self.no_fluid_outputs.get()),
        )

    def _output_chances(self, output_grid: SlotGridFrame) -> list[int]:
        if self.recipe_kind.get() != "machine":
            return []
        return [slot.output_chance for slot in output_grid.slots if slot.item is not None]

    def _special_value(self) -> int | None:
        value = self.special_value_var.get().strip()
        if not value:
            return None
        return int(value)

    def _set_special_item_from_selected_slot(self):
        if self.selected_slot is None or self.selected_slot.item is None:
            self.status_var.set("请先选择一个已有物品的配方格")
            return
        item = self.selected_slot.item
        self.special_item = ScriptItem(item.expression, item.amount, item.comment_name, item.suffix)
        self.special_item_var.set(self.special_item.to_zs())
        self._refresh_preview()

    def _clear_special_item(self):
        self.special_item = None
        self.special_item_var.set("")
        self._refresh_preview()

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

    def _import_script(self):
        path = choose_import_script_file(self.root, self.config.script_output_dir)
        if not path:
            return
        try:
            draft = parse_zs_script(Path(path).read_text(encoding="utf-8-sig"))
            self._load_draft(draft)
            self.config.script_output_dir = str(Path(path).parent)
            self.status_var.set(f"已导入 {Path(path).name}，可以继续编辑")
        except Exception as exc:
            show_error("导入失败", str(exc))

    def _load_draft(self, draft: RecipeDraft):
        self._clear_all_slots()
        self.recipe_kind.set(draft.kind)
        self.remove_mode.set(remove_mode_label(draft.remove_mode))
        self.template_id.set(draft.template_id or "generic_gt_machine")
        self.recipe_map.set(recipe_map_label(draft.recipe_map or self._default_recipe_map(self.template_id.get())))
        self.xp_var.set(str(draft.xp))
        self.include_furnace_xp.set(bool(draft.include_furnace_xp))
        self.shaped_mirrored.set(bool(draft.shaped_mirrored))
        self.fuel_ticks_var.set(str(draft.fuel_ticks))
        self.duration_var.set(str(draft.duration))
        self.eut_var.set(str(draft.eut))
        self.special_value_var.set("" if draft.special_value is None else str(draft.special_value))
        self.special_item = draft.special_item
        self.special_item_var.set("" if draft.special_item is None else draft.special_item.to_zs())
        self.no_fluid_inputs.set(bool(draft.no_fluid_inputs))
        self.no_fluid_outputs.set(bool(draft.no_fluid_outputs))
        self._show_slot_editor(draft.kind)
        self._set_grid_items(self.active_input_grid, draft.item_inputs)
        self._set_grid_items(self.active_output_grid, draft.item_outputs)
        self._set_output_chances(draft.output_chances)
        self.fluid_inputs.set_fluids(draft.fluid_inputs if draft.kind != "remove" else [])
        self.fluid_outputs.set_fluids(draft.fluid_outputs)
        self.remove_fluid_inputs.set_fluids(draft.fluid_inputs if draft.kind == "remove" and draft.remove_mode == "machine" else [])
        self._update_parameter_visibility()
        self._refresh_preview()

    def _set_grid_items(self, grid: SlotGridFrame | None, items: list[ScriptItem | None]):
        if grid is None:
            return
        for slot, item in zip(grid.slots, items):
            slot.set_item(item)

    def _set_output_chances(self, chances: list[int]):
        if self.recipe_kind.get() != "machine" or self.active_output_grid is None:
            return
        for slot, chance in zip([slot for slot in self.active_output_grid.slots if slot.item is not None], chances):
            slot.output_chance = chance

    def _clear_slots(self):
        if self.active_input_grid:
            self.active_input_grid.clear()
        if self.active_output_grid:
            self.active_output_grid.clear()
        self.selected_slot = None
        self._sync_selected_item_options()
        self._refresh_preview()
        self.status_var.set("已清空配方格")

    def _clear_all_slots(self):
        for input_grid, output_grid in self.slot_editors.values():
            input_grid.clear()
            output_grid.clear()
        self.fluid_inputs.set_fluids([])
        self.fluid_outputs.set_fluids([])
        self.remove_fluid_inputs.set_fluids([])
        self.selected_slot = None
        self.special_item = None
        self.special_item_var.set("")
        self._sync_selected_item_options()

    def _on_close(self):
        self.config.window_geometry = self.root.geometry()
        self.config.last_template = self.template_id.get()
        self.config.last_recipe_map = recipe_map_id_from_label(self.recipe_map.get())
        self.config.save(self.config_path)
        self.root.destroy()
