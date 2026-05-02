"""
main.py
HIT137 Group Assignment 3 - Spot the Difference game
"""

import tkinter as tk
from gui import GameWindow


def main():
    root = tk.Tk()
    GameWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
