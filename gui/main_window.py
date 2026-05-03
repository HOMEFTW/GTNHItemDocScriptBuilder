"""Main window for GTNH Item Doc Script Builder."""
from copy import deepcopy
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
    default_recipe_map_for_template,
    normalize_template_id,
    recipe_map_id_from_label,
    recipe_map_label,
    recipe_map_label_options,
    template_id_from_label,
    template_label,
    template_label_options,
)
from core.zs_generator import ZsGenerator
from core.zs_parser import ParsedRecipe, parse_zs_script_matches, parse_zs_script_with_source
from gui.dialogs import AboutDialog, choose_import_script_file, choose_item_index, choose_script_file, show_error, show_info
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


MIN_WINDOW_SIZE = (1400, 1040)
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
        self.app_icon_path = Path(__file__).resolve().parent.parent / "icon.ico"
        self.app_icon_configured = self._configure_icon()
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
        self.template_id = tk.StringVar(value=normalize_template_id(self.config.last_template))
        self.template_label = tk.StringVar(value=template_label(self.template_id.get()))
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
        self.current_draft_source = "当前草稿"
        self.parse_mode_enabled = tk.BooleanVar(value=False)
        self.current_parse_occurrence = 0
        self.current_parse_count = 0
        self.current_parse_start_offset: int | None = None
        self.current_parse_end_offset: int | None = None
        self.recipe_matches: list[ParsedRecipe] = []
        self.saved_drafts: list[RecipeDraft] = []
        self.add_position_var = tk.StringVar(value="文件末尾")
        self.current_script_path: Path | None = None
        self.current_script_path_var = tk.StringVar(value="当前文件: 未命名")
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
        style.configure("Compact.TButton", padding=(6, 3))

    def _configure_icon(self) -> bool:
        if not self.app_icon_path.exists():
            return False
        try:
            self.root.iconbitmap(str(self.app_icon_path))
            return True
        except tk.TclError:
            return False

    def _create_widgets(self):
        main = ttk.Frame(self.root, padding=8)
        main.pack(fill=tk.BOTH, expand=True)

        toolbar = ttk.Frame(main)
        toolbar.pack(fill=tk.X)
        self.toolbar_top = ttk.Frame(toolbar)
        self.toolbar_top.pack(fill=tk.X)
        self.toolbar_bottom = ttk.Frame(toolbar)
        self.toolbar_bottom.pack(fill=tk.X, pady=(3, 0))
        self.choose_index_button = self._toolbar_button(
            self.toolbar_top,
            "选择 item_index.json",
            self._choose_index,
        )
        self.new_script_button = self._toolbar_button(self.toolbar_top, "新建 .zs", self._new_script)
        self.import_button = self._toolbar_button(self.toolbar_top, "导入 .zs", self._import_script)
        self.parse_button = self._toolbar_button(self.toolbar_top, "解析到GUI", self._parse_current_script_to_gui)
        self.disable_parse_button = self._toolbar_button(self.toolbar_top, "关闭解析", self._disable_parse_mode)
        self.first_recipe_button = self._toolbar_button(self.toolbar_top, "第一条", self._parse_first_recipe)
        self.previous_recipe_button = self._toolbar_button(self.toolbar_top, "上一条", self._parse_previous_recipe)
        self.next_recipe_button = self._toolbar_button(self.toolbar_top, "下一条", self._parse_next_recipe)
        self.last_recipe_button = self._toolbar_button(self.toolbar_top, "最后一条", self._parse_last_recipe)
        self.add_to_script_button = self._toolbar_button(self.toolbar_top, "添加到脚本", self._add_generated_to_script)
        self.replace_recipe_button = self._toolbar_button(self.toolbar_top, "替换原配方", self._replace_current_recipe)
        self.save_button = self._toolbar_button(self.toolbar_top, "保存", self._save_script)
        self.save_as_button = self._toolbar_button(self.toolbar_top, "另存为", self._save_script_as)
        self.about_button = self._toolbar_button(self.toolbar_top, "关于", self._show_about, side=tk.RIGHT)
        self.undo_button = self._toolbar_button(self.toolbar_bottom, "撤销", self._undo_full_script)
        self.redo_button = self._toolbar_button(self.toolbar_bottom, "重做", self._redo_full_script)
        self.refresh_preview_button = self._toolbar_button(self.toolbar_bottom, "刷新预览", self._refresh_preview)
        self.copy_preview_button = self._toolbar_button(self.toolbar_bottom, "复制预览", self._copy_preview)
        self.clear_slots_button = self._toolbar_button(self.toolbar_bottom, "清空格子", self._clear_slots)
        self.ore_dictionary_button = self._toolbar_button(self.toolbar_bottom, "填入 OreDict", self._choose_ore_dictionary)
        self._set_ore_dictionary_search_enabled(False)
        self.add_position_label_widget = ttk.Label(self.toolbar_bottom, text="添加位置:")
        self.add_position_label_widget.pack(side=tk.LEFT, padx=(8, 2))
        self.add_position_combo = ttk.Combobox(
            self.toolbar_bottom,
            textvariable=self.add_position_var,
            values=("文件末尾", "当前光标", "当前配方后"),
            state="readonly",
            width=10,
        )
        self.add_position_combo.pack(side=tk.LEFT, padx=2)
        ttk.Label(self.toolbar_bottom, textvariable=self.current_script_path_var, width=48, anchor=tk.W).pack(
            side=tk.RIGHT,
            padx=(8, 0),
        )
        ttk.Label(self.toolbar_bottom, textvariable=self.status_var).pack(side=tk.RIGHT)

        self._create_recipe_match_list(main)
        self._create_saved_draft_list(main)

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

    def _toolbar_button(self, parent, text: str, command, side=tk.LEFT):
        button = ttk.Button(
            parent,
            text=text,
            command=command,
            width=min(max(self._text_display_width(text) + 1, 8), 24),
            style="Compact.TButton",
        )
        button.pack(side=side, padx=2)
        return button

    def _text_display_width(self, text: str) -> int:
        return sum(1 if ord(char) < 128 else 2 for char in text)

    def _create_recipe_match_list(self, parent):
        self.recipe_matches_frame = ttk.LabelFrame(parent, text="配方列表", padding=5)
        self.recipe_matches_frame.pack(fill=tk.X, pady=(6, 0))
        columns = ("index", "line", "kind", "summary")
        self.recipe_match_tree = ttk.Treeview(self.recipe_matches_frame, columns=columns, show="headings", height=4)
        headings = {
            "index": "当前类型",
            "line": "行",
            "kind": "类型",
            "summary": "摘要",
        }
        widths = {"index": 75, "line": 55, "kind": 120, "summary": 980}
        for key in columns:
            self.recipe_match_tree.heading(key, text=headings[key])
            self.recipe_match_tree.column(key, width=widths[key], anchor=tk.W)
        scrollbar = ttk.Scrollbar(self.recipe_matches_frame, orient=tk.VERTICAL, command=self.recipe_match_tree.yview)
        self.recipe_match_tree.configure(yscrollcommand=scrollbar.set)
        self.recipe_match_tree.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.recipe_matches_frame.columnconfigure(0, weight=1)
        self.recipe_matches_frame.rowconfigure(0, weight=1)
        self.recipe_match_tree.bind("<Double-Button-1>", lambda _event: self._parse_selected_recipe_match())
        self.recipe_match_tree.bind("<Return>", lambda _event: self._parse_selected_recipe_match())
        self.recipe_match_tree.bind("<<TreeviewSelect>>", lambda _event: self._parse_selected_recipe_match())

    def _create_saved_draft_list(self, parent):
        self.saved_drafts_frame = ttk.LabelFrame(parent, text="草稿列表", padding=5)
        self.saved_drafts_frame.pack(fill=tk.X, pady=(6, 0))

        buttons = ttk.Frame(self.saved_drafts_frame)
        buttons.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 4))
        self.save_draft_button = self._toolbar_button(buttons, "保存草稿", self._save_current_draft_to_list)
        self.load_draft_button = self._toolbar_button(buttons, "载入草稿", self._load_selected_saved_draft)
        self.delete_draft_button = self._toolbar_button(buttons, "删除草稿", self._delete_selected_saved_draft)
        self.add_all_drafts_button = self._toolbar_button(buttons, "全部添加", self._add_all_saved_drafts_to_script)

        columns = ("index", "kind", "summary")
        self.saved_draft_tree = ttk.Treeview(self.saved_drafts_frame, columns=columns, show="headings", height=3)
        headings = {"index": "序号", "kind": "类型", "summary": "摘要"}
        widths = {"index": 55, "kind": 120, "summary": 1090}
        for key in columns:
            self.saved_draft_tree.heading(key, text=headings[key])
            self.saved_draft_tree.column(key, width=widths[key], anchor=tk.W)
        scrollbar = ttk.Scrollbar(self.saved_drafts_frame, orient=tk.VERTICAL, command=self.saved_draft_tree.yview)
        self.saved_draft_tree.configure(yscrollcommand=scrollbar.set)
        self.saved_draft_tree.grid(row=1, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=1, column=1, sticky=tk.NS)
        self.saved_drafts_frame.columnconfigure(0, weight=1)
        self.saved_drafts_frame.rowconfigure(1, weight=1)
        self.saved_draft_tree.bind("<Double-Button-1>", lambda _event: self._load_selected_saved_draft())
        self.saved_draft_tree.bind("<Return>", lambda _event: self._load_selected_saved_draft())

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
        self.template_label_widget = ttk.Label(params, text="生成方式:")
        self.template_label_widget.grid(row=0, column=0, sticky=tk.W, pady=2)
        self.template_combo = ttk.Combobox(
            params,
            textvariable=self.template_label,
            values=template_label_options(),
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

        self.fluid_inputs = FluidListRowsFrame(parent, "流体输入", 1, self._choose_fluid, self._refresh_preview, adjustable=True)
        self.fluid_inputs.pack(fill=tk.X, pady=4)
        self.fluid_outputs = FluidListRowsFrame(parent, "流体输出", 1, self._choose_fluid, self._refresh_preview, adjustable=True)
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
        if self.parse_mode_enabled.get():
            self._show_slot_editor(self.recipe_kind.get())
            self._update_parameter_visibility()
            self._parse_current_script_to_gui()
            return
        self._show_slot_editor(self.recipe_kind.get())
        self._clear_all_slots()
        self._update_parameter_visibility()
        self._refresh_preview()
        self.status_var.set("已切换脚本类型并清空配方格")

    def _on_remove_mode_selected(self):
        if self.parse_mode_enabled.get() and self.recipe_kind.get() == "remove":
            self._show_slot_editor("remove")
            self._update_parameter_visibility()
            self._parse_current_script_to_gui()
            return
        input_items, output_items, output_chances = self._active_slot_state()
        if self.recipe_kind.get() == "remove":
            self._show_slot_editor("remove")
            self._replace_active_slot_state(input_items, output_items, output_chances)
        self._update_parameter_visibility()
        self._refresh_preview()

    def _active_slot_state(self):
        input_items = self.active_input_grid.items() if self.active_input_grid else []
        output_items = self.active_output_grid.items() if self.active_output_grid else []
        output_chances = [slot.output_chance for slot in self.active_output_grid.slots] if self.active_output_grid else []
        return input_items, output_items, output_chances

    def _replace_active_slot_state(self, input_items, output_items, output_chances):
        if self.active_input_grid:
            self.active_input_grid.clear()
            self._set_grid_items(self.active_input_grid, input_items)
        if self.active_output_grid:
            self.active_output_grid.clear()
            self._set_grid_items(self.active_output_grid, output_items)
            for slot, chance in zip(self.active_output_grid.slots, output_chances):
                slot.output_chance = chance
        self.selected_slot = None
        self._sync_selected_item_options()
        self._update_output_chance_visibility()

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
        self.template_id.set(template_id_from_label(self.template_label.get()))
        self.recipe_map.set(recipe_map_label(self._default_recipe_map(self.template_id.get())))
        self._refresh_preview()

    def _default_recipe_map(self, template_id: str) -> str:
        return default_recipe_map_for_template(template_id)

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
            duration=self._int_field(self.duration_var, "Duration"),
            eut=self._int_field(self.eut_var, "EU/t"),
            special_value=self._special_value(),
            special_item=self.special_item if self.recipe_kind.get() == "machine" else None,
            xp=self._float_field(self.xp_var, "熔炉 XP"),
            include_furnace_xp=bool(self.include_furnace_xp.get()),
            shaped_mirrored=bool(self.shaped_mirrored.get()),
            fuel_ticks=self._int_field(self.fuel_ticks_var, "燃烧时间"),
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

    def _int_field(self, variable: tk.StringVar, label: str) -> int:
        value = variable.get().strip()
        if not value:
            raise ValueError(f"{label} 不能为空")
        try:
            return int(value)
        except ValueError as exc:
            raise ValueError(f"{label} 必须是整数") from exc

    def _float_field(self, variable: tk.StringVar, label: str) -> float:
        value = variable.get().strip()
        if not value:
            raise ValueError(f"{label} 不能为空")
        try:
            return float(value)
        except ValueError as exc:
            raise ValueError(f"{label} 必须是数字") from exc

    def _special_value(self) -> int | None:
        value = self.special_value_var.get().strip()
        if not value:
            return None
        try:
            return int(value)
        except ValueError as exc:
            raise ValueError("Special Value 必须是整数") from exc

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
        self._generate_current_draft_script(blocking=False)

    def _generate_current_draft_script(self, blocking: bool) -> str | None:
        try:
            draft = self._draft()
            script = self._script_for_draft(draft)
            self.preview.set_text(script)
            return script
        except Exception as exc:
            self.preview.set_text(f"// 无法生成脚本: {exc}")
            if blocking:
                self.status_var.set(f"草稿校验失败: {exc}")
            return None

    def _script_for_draft(self, draft: RecipeDraft) -> str:
        generated = self.generator.generate(draft)
        comment = self._draft_comment(draft)
        return f"// {comment}\n{generated}" if comment else generated

    def _save_current_draft_to_list(self):
        try:
            draft = self._draft()
            self.preview.set_text(self._script_for_draft(draft))
        except Exception as exc:
            self.preview.set_text(f"// 无法生成脚本: {exc}")
            self.status_var.set(f"草稿校验失败: {exc}")
            return
        self.saved_drafts.append(deepcopy(draft))
        self._refresh_saved_draft_list()
        self.status_var.set(f"已保存草稿 {len(self.saved_drafts)}")

    def _refresh_saved_draft_list(self):
        if not hasattr(self, "saved_draft_tree"):
            return
        self.saved_draft_tree.delete(*self.saved_draft_tree.get_children())
        for index, draft in enumerate(self.saved_drafts):
            self.saved_draft_tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(str(index + 1), self._draft_kind_label(draft), self._draft_summary(draft)),
            )

    def _load_selected_saved_draft(self):
        selection = self.saved_draft_tree.selection()
        if not selection:
            self.status_var.set("请先选择一个草稿")
            return
        index = int(selection[0])
        if index < 0 or index >= len(self.saved_drafts):
            return
        self.current_draft_source = f"当前草稿: 草稿 {index + 1}"
        self.preview.set_source_label(self.current_draft_source)
        self._load_draft(deepcopy(self.saved_drafts[index]))
        self.status_var.set(f"已载入草稿 {index + 1}")

    def _delete_selected_saved_draft(self):
        selection = self.saved_draft_tree.selection()
        if not selection:
            self.status_var.set("请先选择一个草稿")
            return
        index = int(selection[0])
        if index < 0 or index >= len(self.saved_drafts):
            return
        del self.saved_drafts[index]
        self._refresh_saved_draft_list()
        self.status_var.set("已删除草稿")

    def _add_all_saved_drafts_to_script(self):
        if not self.saved_drafts:
            self.status_var.set("草稿列表为空")
            return
        scripts = [self._script_for_draft(draft) for draft in self.saved_drafts]
        existing = self.preview.get_full_text().rstrip()
        separator = "\n\n" if existing else ""
        self.preview.full_text.insert("end-1c", separator + "\n\n".join(scripts))
        self.status_var.set(f"已添加 {len(self.saved_drafts)} 条草稿到完整脚本")

    def _copy_preview(self):
        text = self.preview.get_text()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set("已复制 ZS 预览")

    def _show_about(self):
        AboutDialog(self.root)

    def _new_script(self):
        path = choose_script_file(self.root, self.config.script_output_dir)
        if not path:
            return
        try:
            save_script(path, "")
            self.preview.set_full_text("")
            self._reset_parse_state()
            self._set_current_script_path(Path(path))
            self.config.script_output_dir = str(Path(path).parent)
            self.current_draft_source = "当前草稿: 新建脚本"
            self.preview.set_source_label(self.current_draft_source)
            self._clear_recipe_match_list()
            self.status_var.set(f"已新建 {Path(path).name}")
            show_info("新建成功", path)
        except Exception as exc:
            show_error("新建失败", str(exc))

    def _save_script(self):
        self._refresh_preview()
        if self.current_script_path is None:
            self._save_script_as()
            return
        self._write_script_to_path(self.current_script_path, "保存成功")

    def _save_script_as(self):
        self._refresh_preview()
        path = choose_script_file(self.root, self.config.script_output_dir)
        if not path:
            return
        self._write_script_to_path(Path(path), "另存为成功")

    def _write_script_to_path(self, path: Path, success_title: str):
        try:
            save_script(path, self._save_content())
            self._set_current_script_path(Path(path))
            self.config.script_output_dir = str(Path(path).parent)
            self.status_var.set(f"已保存 {Path(path).name}")
            show_info(success_title, str(path))
        except Exception as exc:
            show_error("保存失败", str(exc))

    def _save_content(self) -> str:
        return self.preview.get_full_text()

    def _import_script(self):
        path = choose_import_script_file(self.root, self.config.script_output_dir)
        if not path:
            return
        try:
            script_text = Path(path).read_text(encoding="utf-8-sig")
            self._load_script_text(script_text, Path(path).name, Path(path))
            self.config.script_output_dir = str(Path(path).parent)
            self.status_var.set(f"已导入 {Path(path).name}，可以继续编辑")
        except Exception as exc:
            show_error("导入失败", str(exc))

    def _load_script_text(self, script_text: str, filename: str, path: Path | None = None):
        self._reset_parse_state()
        self.preview.set_full_text(script_text)
        self._set_current_script_path(path, filename)
        self.current_draft_source = f"当前草稿: {filename} 未解析"
        self.preview.set_source_label(self.current_draft_source)
        self._clear_recipe_match_list()

    def _reset_parse_state(self):
        self.parse_mode_enabled.set(False)
        self.current_parse_occurrence = 0
        self.current_parse_count = 0
        self.current_parse_start_offset = None
        self.current_parse_end_offset = None
        self.recipe_matches = []

    def _set_current_script_path(self, path: Path | None, label: str | None = None):
        self.current_script_path = path
        if path is None:
            self.current_script_path_var.set("当前文件: 未命名")
            self.preview.set_full_label(label or "未命名 .zs")
            return
        self.current_script_path_var.set(f"当前文件: {path}")
        self.preview.set_full_label(path.name)

    def _parse_current_script_to_gui(self):
        self.current_parse_occurrence = 0
        self._parse_script_occurrence(0)

    def _parse_script_occurrence(self, occurrence: int):
        try:
            self._refresh_recipe_match_list()
            parsed = parse_zs_script_with_source(
                self.preview.get_full_text(),
                self._allowed_parse_kinds(),
                occurrence=occurrence,
            )
            self.current_parse_occurrence = parsed.parseable_index - 1
            self.current_parse_count = parsed.parseable_count
            self.current_parse_start_offset = parsed.start_offset
            self.current_parse_end_offset = parsed.end_offset
            self.current_draft_source = (
                f"当前草稿: 第 {parsed.parseable_index}/{parsed.parseable_count} 条当前类型，"
                f"全脚本第 {parsed.recipe_number} 条受支持配方，行 {parsed.line_number} ({parsed.marker})"
            )
            self.preview.set_source_label(self.current_draft_source)
            self._load_draft(parsed.draft)
            self.parse_mode_enabled.set(True)
            self.status_var.set(self.current_draft_source)
        except Exception as exc:
            show_error("解析失败", str(exc))

    def _refresh_recipe_match_list(self):
        self._clear_recipe_match_list()
        try:
            self.recipe_matches = parse_zs_script_matches(self.preview.get_full_text(), self._allowed_parse_kinds())
        except Exception as exc:
            self.recipe_matches = []
            self.status_var.set(f"配方列表解析失败：{exc}")
            return
        for index, parsed in enumerate(self.recipe_matches):
            self.recipe_match_tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    f"{parsed.parseable_index}/{parsed.parseable_count}",
                    str(parsed.line_number),
                    self._draft_kind_label(parsed.draft),
                    self._draft_summary(parsed.draft),
                ),
            )

    def _clear_recipe_match_list(self):
        if hasattr(self, "recipe_match_tree"):
            self.recipe_match_tree.delete(*self.recipe_match_tree.get_children())

    def _parse_selected_recipe_match(self):
        selection = self.recipe_match_tree.selection()
        if not selection:
            return
        self._parse_script_occurrence(int(selection[0]))

    def _parse_first_recipe(self):
        self._parse_script_occurrence(0)

    def _parse_previous_recipe(self):
        self._parse_script_occurrence(max(self.current_parse_occurrence - 1, 0))

    def _parse_next_recipe(self):
        self._parse_script_occurrence(self.current_parse_occurrence + 1)

    def _parse_last_recipe(self):
        self._parse_script_occurrence(-1)

    def _disable_parse_mode(self):
        self.parse_mode_enabled.set(False)
        self.status_var.set("解析已关闭：切换脚本类型时保留当前草稿")

    def _draft_kind_label(self, draft: RecipeDraft) -> str:
        if draft.kind == "machine":
            return "GTNH/模组机器"
        if draft.kind == "shaped":
            return "有序合成"
        if draft.kind == "shapeless":
            return "无序合成"
        if draft.kind == "furnace":
            return "熔炉"
        if draft.kind == "fuel":
            return "燃料"
        if draft.kind == "remove":
            return f"删除-{remove_mode_label(draft.remove_mode)}"
        return draft.kind

    def _draft_summary(self, draft: RecipeDraft) -> str:
        outputs = [self._item_comment(item) for item in draft.item_outputs if item is not None]
        inputs = [self._item_comment(item) for item in draft.item_inputs if item is not None]
        fluid_inputs = [self._fluid_comment(fluid) for fluid in draft.fluid_inputs]
        fluid_outputs = [self._fluid_comment(fluid) for fluid in draft.fluid_outputs]
        if draft.kind == "machine":
            all_inputs = inputs + fluid_inputs
            all_outputs = outputs + fluid_outputs
            return (
                f"{draft.recipe_map or 'gt.recipe.assembler'}: "
                f"{self._join_comment_parts(all_inputs) or '无输入'} -> {self._join_comment_parts(all_outputs) or '无输出'}"
            )
        if draft.kind == "remove":
            target = self._join_comment_parts(outputs or inputs)
            return f"删除 {target or draft.recipe_map or '配方'}"
        if draft.kind == "fuel":
            return f"{inputs[0] if inputs else '燃料'} -> {draft.fuel_ticks} ticks"
        return f"{self._join_comment_parts(outputs) or '无输出'} <- {self._join_comment_parts(inputs) or '无输入'}"

    def _draft_comment(self, draft: RecipeDraft) -> str:
        outputs = [self._item_comment(item) for item in draft.item_outputs if item is not None]
        inputs = [self._item_comment(item) for item in draft.item_inputs if item is not None]
        fluid_inputs = [self._fluid_comment(fluid) for fluid in draft.fluid_inputs]
        fluid_outputs = [self._fluid_comment(fluid) for fluid in draft.fluid_outputs]
        if draft.kind == "shaped":
            action = "镜像有序合成" if draft.shaped_mirrored else "有序合成"
            return f"{self._join_comment_parts(inputs)} {action} {self._join_comment_parts(outputs)}"
        if draft.kind == "shapeless":
            return f"{self._join_comment_parts(inputs)} 无序合成 {self._join_comment_parts(outputs)}"
        if draft.kind == "furnace":
            return f"{self._join_comment_parts(inputs)} 熔炉烧制 {self._join_comment_parts(outputs)}"
        if draft.kind == "fuel":
            return f"{self._join_comment_parts(inputs)} 作为燃料燃烧 {draft.fuel_ticks} ticks"
        if draft.kind == "machine":
            all_inputs = inputs + fluid_inputs
            all_outputs = outputs + fluid_outputs
            return (
                f"{self._join_comment_parts(all_inputs)} 通过 "
                f"{draft.recipe_map or 'gt.recipe.assembler'} 合成 {self._join_comment_parts(all_outputs)}"
            )
        if draft.kind == "remove":
            return self._draft_summary(draft)
        return ""

    def _item_comment(self, item: ScriptItem) -> str:
        expression = item.expression.strip()
        name = f"{item.comment_name.strip()} {expression}" if item.comment_name.strip() else expression
        suffix = item.suffix.strip()
        if suffix and not item.comment_name.strip():
            name += suffix
        return f"{name} * {item.amount}"

    def _fluid_comment(self, fluid: ScriptFluid) -> str:
        expression = fluid.to_zs().rsplit(" * ", 1)[0]
        name = f"{fluid.comment_name.strip()} {expression}" if fluid.comment_name.strip() else fluid.name_or_expression.strip()
        return f"{name} * {fluid.amount}"

    def _join_comment_parts(self, parts: list[str]) -> str:
        return " 和 ".join(parts)

    def _allowed_parse_kinds(self) -> set[str]:
        kind = self.recipe_kind.get()
        if kind != "remove":
            return {kind}
        remove_mode = remove_mode_id_from_label(self.remove_mode.get())
        if remove_mode == "machine":
            return {"remove_machine"}
        if remove_mode == "furnace":
            return {"remove_furnace"}
        if remove_mode == "shaped":
            return {"remove_shaped"}
        if remove_mode == "shapeless":
            return {"remove_shapeless"}
        return {"remove_all"}

    def _add_generated_to_script(self):
        generated = self._generate_current_draft_script(blocking=True)
        generated = "" if generated is None else generated.strip()
        if not generated:
            return
        position = self.add_position_var.get()
        if position == "当前光标":
            self.preview.full_text.insert("insert", generated)
        elif position == "当前配方后" and self.current_parse_end_offset is not None:
            self.preview.full_text.insert(self._full_text_index(self.current_parse_end_offset), "\n\n" + generated)
        else:
            existing = self.preview.get_full_text().rstrip()
            separator = "\n\n" if existing else ""
            self.preview.full_text.insert("end-1c", separator + generated)
        self.status_var.set("已添加当前草稿到完整脚本")

    def _replace_current_recipe(self):
        generated = self._generate_current_draft_script(blocking=True)
        generated = "" if generated is None else generated.strip()
        if not generated:
            return
        if self.current_parse_start_offset is None or self.current_parse_end_offset is None:
            self.status_var.set("没有可替换的已解析配方")
            return
        self.preview.full_text.delete(
            self._full_text_index(self.current_parse_start_offset),
            self._full_text_index(self.current_parse_end_offset),
        )
        self.preview.full_text.insert(self._full_text_index(self.current_parse_start_offset), generated)
        self.current_parse_end_offset = self.current_parse_start_offset + len(generated)
        self._refresh_recipe_match_list()
        self.status_var.set("已替换原配方")

    def _full_text_index(self, offset: int) -> str:
        return f"1.0+{offset}c"

    def _undo_full_script(self):
        try:
            self.preview.full_text.edit_undo()
        except tk.TclError:
            pass

    def _redo_full_script(self):
        try:
            self.preview.full_text.edit_redo()
        except tk.TclError:
            pass

    def _load_draft(self, draft: RecipeDraft):
        self._clear_all_slots()
        self.recipe_kind.set(draft.kind)
        self.remove_mode.set(remove_mode_label(draft.remove_mode))
        draft_template_id = draft.template_id or "generic_gt_machine"
        self.template_id.set(normalize_template_id(draft_template_id))
        self.template_label.set(template_label(self.template_id.get()))
        self.recipe_map.set(recipe_map_label(draft.recipe_map or self._default_recipe_map(draft_template_id)))
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
