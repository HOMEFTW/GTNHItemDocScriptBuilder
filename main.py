#!/usr/bin/env python3
"""GTNH Item Doc Script Builder."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow


def main():
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
