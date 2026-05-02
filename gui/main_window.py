"""Main window for GTNH Item Doc Script Builder."""
import tkinter as tk
from tkinter import ttk


class MainWindow:
    TITLE = "GTNH 脚本生成器"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(self.TITLE)
        self.root.geometry("1200x820")
        ttk.Label(self.root, text="GTNH 脚本生成器").pack(padx=20, pady=20)

    def run(self):
        self.root.mainloop()
