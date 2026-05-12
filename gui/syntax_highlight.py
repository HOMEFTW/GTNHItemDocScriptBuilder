"""ZenScript syntax highlighting for tk.Text widgets."""
import re
import tkinter as tk


class ZsSyntaxHighlighter:
    """Applies ZenScript syntax highlighting via text tags, with live update on edits."""

    PATTERNS = [
        ("comment", r"//[^\n]*"),
        ("string", r'"[^"\\]*(?:\\.[^"\\]*)*"'),
        ("angle_bracket", r"<[^>]+>"),
        ("keyword", r"\b(?:val|var|import|function|return|if|else|for|while|in|as|null|true|false)\b"),
        ("method", r"\.\w+(?=\s*\()"),
        ("number", r"\b\d+(?:\.\d+)?\b"),
    ]

    TAG_CONFIG = {
        "comment": {"foreground": "#6b7280"},
        "string": {"foreground": "#059669"},
        "number": {"foreground": "#2563eb"},
        "keyword": {"foreground": "#7c3aed", "font": ("Consolas", 10, "bold")},
        "method": {"foreground": "#b45309"},
        "angle_bracket": {"foreground": "#dc2626"},
    }

    DEBOUNCE_MS = 200

    def __init__(self, text_widget: tk.Text, live: bool = False):
        self.text = text_widget
        self._after_id: str | None = None
        for tag, config in self.TAG_CONFIG.items():
            self.text.tag_configure(tag, **config)
        self.text.tag_raise("comment")
        if live:
            self.text.bind("<<Modified>>", self._on_modified, add="+")

    def _on_modified(self, _event):
        if not self.text.edit_modified():
            return
        self.text.edit_modified(False)
        if self._after_id is not None:
            self.text.after_cancel(self._after_id)
        self._after_id = self.text.after(self.DEBOUNCE_MS, self._deferred_highlight)

    def _deferred_highlight(self):
        self._after_id = None
        self.highlight()

    def highlight(self):
        content = self.text.get("1.0", tk.END)
        for tag in self.TAG_CONFIG:
            self.text.tag_remove(tag, "1.0", tk.END)
        for tag, pattern in self.PATTERNS:
            for match in re.finditer(pattern, content):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text.tag_add(tag, start, end)
