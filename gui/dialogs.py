"""Dialog helpers."""
from pathlib import Path
from tkinter import filedialog, messagebox


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
