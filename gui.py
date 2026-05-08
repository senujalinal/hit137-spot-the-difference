"""
gui.py
HIT137 Group Assignment 3

Main tkinter GUI - side by side image display.
Still working on click detection and game logic.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk

from image_processor import ImageProcessor
from game_state import GameState

# colours
BG_DARK = "#0D1117"
PANEL_BG = "#161B22"
CARD_BG = "#1C2128"
BORDER = "#30363D"
ACCENT = "#7C3AED"
ACCENT2 = "#06B6D4"
SUCCESS = "#3FB950"
DANGER = "#F85149"
WARNING = "#D29922"
TEXT_PRIMARY = "#E6EDF3"
TEXT_MUTED = "#8B949E"

CANVAS_W = 510
CANVAS_H = 510
FOUND_COLOUR = "#FF3B3B"
REVEAL_COLOUR = "#2E86FF"
WRONG_COLOUR = "#FF8C00"
CIRCLE_WIDTH = 3


class ImageCanvas(tk.Canvas):
    """Canvas widget that shows one image and draws difference circles."""

    def __init__(self, parent, label_text, **kwargs):
        super().__init__(
            parent,
            width=CANVAS_W,
            height=CANVAS_H,
            bg=CARD_BG,
            highlightthickness=1,
            highlightbackground=BORDER,
            **kwargs,
        )
        self._label_text = label_text
        self._photo_image = None
        self._scale = 1.0
        self._offset_x = 0
        self._offset_y = 0
        self._draw_placeholder()

    def set_image(self, bgr_image):
        """Display BGR image scaled to fit canvas with correct aspect ratio."""
        self.delete("all")
        rgb = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        img_h, img_w = rgb.shape[:2]

        self._scale = min(CANVAS_W / img_w, CANVAS_H / img_h)
        disp_w = int(img_w * self._scale)
        disp_h = int(img_h * self._scale)
        self._offset_x = (CANVAS_W - disp_w) // 2
        self._offset_y = (CANVAS_H - disp_h) // 2

        pil = Image.fromarray(rgb).resize((disp_w, disp_h), Image.LANCZOS)
        self._photo_image = ImageTk.PhotoImage(pil)
        self.create_image(CANVAS_W // 2, CANVAS_H // 2,
                          image=self._photo_image, anchor="center")

    def draw_circle(self, region, colour, tag="", label=""):
        """Draw circle around a difference region on the canvas."""
        x, y, w, h = region
        cx = self._offset_x + int((x + w / 2) * self._scale)
        cy = self._offset_y + int((y + h / 2) * self._scale)
        r = max(28, int(max(w, h) * self._scale / 2) + 8)
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         outline=colour, width=CIRCLE_WIDTH, tags=tag)
        if label:
            self.create_text(cx, cy, text=label, fill=colour,
                             font=("Helvetica", 11, "bold"), tags=tag)

    def flash_cross(self, canvas_x, canvas_y):
        """Flash a cross at wrong click position, auto-removes after 600ms."""
        s = 14
        tag = "wrong_flash"
        self.create_line(canvas_x - s, canvas_y - s,
                         canvas_x + s, canvas_y + s,
                         fill=WRONG_COLOUR, width=3, tags=tag)
        self.create_line(canvas_x + s, canvas_y - s,
                         canvas_x - s, canvas_y + s,
                         fill=WRONG_COLOUR, width=3, tags=tag)
        self.after(600, lambda: self.delete(tag))

    def canvas_to_image_coords(self, canvas_x, canvas_y):
        """Convert canvas pixel coords to original image coords."""
        ix = int((canvas_x - self._offset_x) / self._scale)
        iy = int((canvas_y - self._offset_y) / self._scale)
        return ix, iy

    def _draw_placeholder(self):
        mid_x, mid_y = CANVAS_W // 2, CANVAS_H // 2
        self.create_rectangle(30, 30, CANVAS_W - 30, CANVAS_H - 30,
                              outline=BORDER, dash=(6, 4), width=1)
        self.create_text(mid_x, mid_y - 18, text="🖼",
                         font=("Helvetica", 32), fill=TEXT_MUTED)
        self.create_text(mid_x, mid_y + 26, text=self._label_text,
                         font=("Helvetica", 13), fill=TEXT_MUTED, justify="center")


class GameWindow:
    """Main application window. Connects ImageProcessor and GameState to the GUI."""

    TITLE = "Spot the Difference - HIT137"
    MIN_W = 1160
    MIN_H = 720

    def __init__(self, root):
        self._root = root
        self._processor = ImageProcessor()
        self._state = GameState()
        self._configure_window()
        self._build_ui()

    def _configure_window(self):
        self._root.title(self.TITLE)
        self._root.configure(bg=BG_DARK)
        self._root.minsize(self.MIN_W, self.MIN_H)
        self._root.update_idletasks()
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        x = (sw - self.MIN_W) // 2
        y = (sh - self.MIN_H) // 2
        self._root.geometry(f"{self.MIN_W}x{self.MIN_H}+{x}+{y}")

    def _build_ui(self):
        self._build_header()
        self._build_toolbar()
        self._build_canvases()
        self._build_status_bar()

    def _build_header(self):
        bar = tk.Frame(self._root, bg=PANEL_BG, pady=14)
        bar.pack(fill="x")
        tk.Label(bar, text="🔍  Spot the Difference",
                 font=("Helvetica", 20, "bold"),
                 fg=TEXT_PRIMARY, bg=PANEL_BG).pack(side="left", padx=24)
        self._score_var = tk.StringVar(value="Total Score: 0")
        tk.Label(bar, textvariable=self._score_var,
                 font=("Helvetica", 13, "bold"),
                 fg=ACCENT2, bg=PANEL_BG, padx=16).pack(side="right", padx=24)

    def _build_toolbar(self):
        bar = tk.Frame(self._root, bg=BG_DARK, pady=10)
        bar.pack(fill="x", padx=20)
        btn_kw = dict(font=("Helvetica", 12, "bold"), relief="flat",
                      cursor="hand2", padx=18, pady=7, bd=0)

        self._load_btn = tk.Button(bar, text="📂  Load Image",
                                   bg=ACCENT, fg="white",
                                   activebackground="#6D28D9",
                                   activeforeground="white",
                                   command=self._on_load_image, **btn_kw)
        self._load_btn.pack(side="left", padx=(0, 10))

        self._reveal_btn = tk.Button(bar, text="👁  Reveal All",
                                     bg=PANEL_BG, fg=TEXT_MUTED,
                                     activebackground=CARD_BG,
                                     activeforeground=TEXT_PRIMARY,
                                     command=self._on_reveal,
                                     state="disabled", **btn_kw)
        self._reveal_btn.pack(side="left", padx=(0, 10))

        hud = tk.Frame(bar, bg=BG_DARK)
        hud.pack(side="right")

        self._remaining_var = tk.StringVar(value="Remaining: —")
        tk.Label(hud, textvariable=self._remaining_var,
                 font=("Helvetica", 13, "bold"),
                 fg=ACCENT2, bg=BG_DARK, padx=14).pack(side="left")

        tk.Label(hud, text="│", fg=BORDER, bg=BG_DARK).pack(side="left")

        self._mistakes_var = tk.StringVar(value="Mistakes: 0 / 3")
        self._mistakes_lbl = tk.Label(hud, textvariable=self._mistakes_var,
                                      font=("Helvetica", 13, "bold"),
                                      fg=TEXT_MUTED, bg=BG_DARK, padx=14)
        self._mistakes_lbl.pack(side="left")

    def _build_canvases(self):
        area = tk.Frame(self._root, bg=BG_DARK)
        area.pack(fill="both", expand=True, padx=20, pady=(4, 6))

        left = tk.Frame(area, bg=BG_DARK)
        left.pack(side="left", expand=True, fill="both", padx=(0, 8))
        tk.Label(left, text="Original Image",
                 font=("Helvetica", 11, "bold"),
                 fg=TEXT_MUTED, bg=BG_DARK).pack(pady=(0, 4))
        self._orig_canvas = ImageCanvas(left, "Original Image\n(reference only)")
        self._orig_canvas.pack()

        right = tk.Frame(area, bg=BG_DARK)
        right.pack(side="right", expand=True, fill="both", padx=(8, 0))
        tk.Label(right, text="Modified Image  ← Click here to find differences",
                 font=("Helvetica", 11, "bold"),
                 fg=ACCENT2, bg=BG_DARK).pack(pady=(0, 4))
        self._mod_canvas = ImageCanvas(right, "Modified Image\n← Click to find differences")
        self._mod_canvas.pack()
        self._mod_canvas.bind("<Button-1>", self._on_canvas_click)

    def _build_status_bar(self):
        self._status_var = tk.StringVar(value="  Load an image to start playing.")
        tk.Label(self._root, textvariable=self._status_var,
                 font=("Helvetica", 11), fg=TEXT_MUTED, bg=PANEL_BG,
                 anchor="w", padx=20, pady=8).pack(fill="x", side="bottom")

    def _on_load_image(self):
        path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=ImageProcessor.SUPPORTED_FORMATS)
        if not path:
            return
        if not self._processor.load_image(path):
            messagebox.showerror("Error", "Could not open image.")
            return
        self._state.reset_round()
        self._orig_canvas.set_image(self._processor.original_bgr)
        self._mod_canvas.set_image(self._processor.modified_bgr)
        self._reveal_btn.config(state="normal", bg=PANEL_BG, fg=TEXT_PRIMARY)
        self._update_hud()
        self._set_status("  Image loaded! Click the modified image to find the 5 differences.")

    def _on_canvas_click(self, event):
        if self._processor.original_bgr is None:
            return
        if self._state.is_round_over:
            return
        ix, iy = self._mod_canvas.canvas_to_image_coords(event.x, event.y)
        result = self._state.process_click(ix, iy, self._processor.alterations)

        if result["hit"]:
            idx = result["index"]
            region = self._processor.alterations[idx].region
            label = str(self._state.found_count)
            self._orig_canvas.draw_circle(region, FOUND_COLOUR, tag="found", label=label)
            self._mod_canvas.draw_circle(region, FOUND_COLOUR, tag="found", label=label)
            if result["complete"]:
                self._on_round_complete()
            else:
                self._set_status(f"  ✅  Found one! {self._state.remaining} remaining.")
        elif result["mistake"]:
            self._mod_canvas.flash_cross(event.x, event.y)
            if result["locked_out"]:
                self._on_locked_out()
            else:
                self._set_status(
                    f"  ❌  Wrong spot. {self._state.mistakes_remaining} guesses left.")
        self._update_hud()

    def _on_reveal(self):
        if self._processor.original_bgr is None:
            return
        self._state.reveal_all()
        self._draw_revealed_circles()
        self._reveal_btn.config(state="disabled")
        found = self._state.found_count
        self._set_status(
            f"  Differences revealed. You found {found} of 5. Load a new image to continue.")
        self._update_hud()

    def _on_round_complete(self):
        self._reveal_btn.config(state="disabled")
        self._set_status(
            f"  🎉 All 5 found! Cumulative score: {self._state.total_score}. Load a new image.")
        messagebox.showinfo("Round Complete! 🎉",
                            f"You found all 5 differences!\n\n"
                            f"Cumulative score: {self._state.total_score}")

    def _on_locked_out(self):
        self._draw_revealed_circles()
        self._reveal_btn.config(state="disabled")
        found = self._state.found_count
        self._set_status(
            f"  ⛔ Too many mistakes! You found {found} of 5. Load a new image to try again.")
        messagebox.showwarning("Too Many Mistakes ⛔",
                               f"You used all 3 guesses.\n\n"
                               f"You found {found} of 5 differences this round.\n\n"
                               "Remaining differences shown in blue.\n"
                               "Load a new image to play again.")

    def _update_hud(self):
        self._score_var.set(f"Total Score: {self._state.total_score}")
        self._remaining_var.set(f"Remaining: {self._state.remaining}")
        m = self._state.mistakes
        self._mistakes_var.set(f"Mistakes: {m} / {GameState.MAX_MISTAKES}")
        if m == 0:
            colour = TEXT_MUTED
        elif m < GameState.MAX_MISTAKES:
            colour = WARNING
        else:
            colour = DANGER
        self._mistakes_lbl.config(fg=colour)

    def _draw_revealed_circles(self):
        found = self._state.found_indices
        for idx, alt in enumerate(self._processor.alterations):
            if idx not in found:
                self._orig_canvas.draw_circle(alt.region, REVEAL_COLOUR, tag="revealed")
                self._mod_canvas.draw_circle(alt.region, REVEAL_COLOUR, tag="revealed")

    def _set_status(self, msg):
        self._status_var.set(msg)
