"""Dialog helpers."""
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


APP_NAME = "GTNHItemDocScriptBuilder"
APP_VERSION = "1.0.0"
APP_STUDIO = "Andgatech"


def choose_item_index(parent, initial: str = "") -> str:
    initial_path = Path(initial) if initial else Path()
    return filedialog.askopenfilename(
        parent=parent,
        title="选择 item_index.json",
        initialdir=str(initial_path.parent) if initial_path.parent != Path(".") else "",
        initialfile=initial_path.name,
        filetypes=[("Item index", "item_index.json"), ("JSON", "*.json"), ("All files", "*.*")],
    )


def choose_script_file(parent, initial_dir: str = "") -> str:
    return filedialog.asksaveasfilename(
        parent=parent,
        title="保存 ZS 脚本",
        initialdir=initial_dir,
        initialfile="andgatech_recipes.zs",
        defaultextension=".zs",
        filetypes=[("CraftTweaker script", "*.zs"), ("All files", "*.*")],
    )


def choose_import_script_file(parent, initial_dir: str = "") -> str:
    return filedialog.askopenfilename(
        parent=parent,
        title="导入 ZS 脚本",
        initialdir=initial_dir,
        filetypes=[("CraftTweaker script", "*.zs"), ("All files", "*.*")],
    )


def show_error(title: str, message: str) -> None:
    messagebox.showerror(title, message)


def show_info(title: str, message: str) -> None:
    messagebox.showinfo(title, message)


class AboutDialog(tk.Toplevel):
    """Application information dialog."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("关于")
        self.parent = parent
        self._create_widgets()
        self._center_window()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text=APP_NAME, font=("Arial", 14, "bold")).pack()
        ttk.Label(main_frame, text=f"版本 {APP_VERSION}").pack(pady=5)
        ttk.Label(main_frame, text="GTNH CraftTweaker / ModTweaker 脚本生成器").pack(pady=10)
        ttk.Label(main_frame, text=f"工作室 {APP_STUDIO}").pack(pady=2)
        ttk.Label(main_frame, text="© 2026").pack()

        ttk.Button(main_frame, text="确定", command=self.destroy).pack(pady=10)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _center_window(self):
        self.transient(self.parent)
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - width) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")
