"""Debounce utility for Tkinter callbacks."""
import tkinter as tk
from typing import Callable


class DebouncedCallback:
    """Delays callback execution; resets timer on each call."""

    def __init__(self, widget: tk.Widget, delay_ms: int, callback: Callable):
        self._widget = widget
        self._delay_ms = delay_ms
        self._callback = callback
        self._after_id: str | None = None

    def __call__(self, *args):
        if self._after_id is not None:
            self._widget.after_cancel(self._after_id)
        self._after_id = self._widget.after(self._delay_ms, lambda: self._fire(*args))

    def _fire(self, *args):
        self._after_id = None
        self._callback(*args)

    def cancel(self):
        if self._after_id is not None:
            self._widget.after_cancel(self._after_id)
            self._after_id = None
