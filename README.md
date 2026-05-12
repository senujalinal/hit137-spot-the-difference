# HIT137 — Group Assignment 3: Spot the Difference

A fully-featured desktop "Spot the Difference" game built with **Python 3**, **Tkinter**, and **OpenCV**, satisfying all requirements of HIT137 Group Assignment 3.

---

## Quick Start

### 1. Install dependencies

```bash
pip3 install opencv-python pillow numpy
```

> **macOS (Homebrew Python 3.13)** — also run:
> ```bash
> brew install python-tk@3.13
> ```

### 2. Generate the built-in sample image *(optional)*

```bash
python3.13 sample_generator.py
```

This creates `sample_image.png` — a colourful geometric scene you can load immediately without sourcing your own photograph.

### 3. Launch the game

```bash
python3.13 main.py
```

---

## How to Play

| Step | Action |
|------|--------|
| 1 | Click **📂 Load Image** and choose any JPG, PNG, or BMP file |
| 2 | The **Original** image appears on the left (reference only) |
| 3 | Click the **Modified** image on the right to locate differences |
| 4 | A **red circle** appears on **both** images when you find one |
| 5 | Find all **5** differences to complete the round |
| 6 | You have **3 incorrect clicks** before the round locks out |
| 7 | Press **👁 Reveal All** at any time to show remaining differences in **blue** |
| 8 | Load a new image to keep playing — your score is cumulative |

---

## Project Structure

```
spot-the-difference/
├── main.py               # Application entry point
├── image_processor.py    # OpenCV image loading + difference injection
├── game_state.py         # Game logic (clicks, mistakes, scoring)
├── gui.py                # Tkinter GUI (ImageCanvas + GameWindow)
├── sample_generator.py   # Generates a built-in test image via OpenCV
├── sample_image.png      # Pre-generated sample image
├── github_link.txt       # GitHub repository URL (for submission)
└── README.md             # This file
```

---

## OOP Design

### Class Hierarchy

```
Alteration  ← abstract base (inheritance, polymorphism)
├── ColourShiftAlteration   hue rotation in HSV colour space
├── BlurAlteration          Gaussian blur (cv2.GaussianBlur)
├── BrightnessAlteration    brightness delta (cv2.convertScaleAbs)
└── SaturationAlteration    saturation shift in HSV colour space

tk.Canvas  ← Tkinter built-in
└── ImageCanvas             display + overlay drawing (inheritance)

ImageProcessor              image I/O and difference orchestration
GameState                   click detection, mistakes, cumulative score
GameWindow                  GUI shell; composes ImageProcessor + GameState
```

### OOP Principles

| Principle | Implementation |
|-----------|---------------|
| **Encapsulation** | All state is `_private`; exposed read-only via `@property` |
| **Inheritance** | `ImageCanvas` extends `tk.Canvas`; four alteration types extend `Alteration` |
| **Polymorphism** | `alteration.apply(img)` called uniformly regardless of concrete subtype |
| **Constructors** | Every class has `__init__` with typed, documented parameters |
| **Class interaction** | `GameWindow` drives `ImageProcessor` + `GameState`; they do not know about each other |
| **≥ 3 classes** | 9 distinct classes across 4 modules |

---

## Image Processing (OpenCV)

All pixel-level work uses **OpenCV** exclusively:

| Alteration | OpenCV technique |
|------------|-----------------|
| Colour Shift | `cv2.cvtColor` (BGR↔HSV), hue channel rotation |
| Blur | `cv2.GaussianBlur` with random odd kernel (11–17) |
| Brightness | `cv2.convertScaleAbs(alpha=1.0, beta=±30–60)` |
| Saturation | `cv2.cvtColor` (BGR↔HSV), saturation channel clamp-shift |

**Non-overlap guarantee:** rejection sampling with AABB separation testing + 15 px padding ensures all 5 regions are visually distinct every load.

---

## Gameplay Features (Tkinter GUI)

| Requirement | Status |
|-------------|--------|
| Load image — JPG, PNG, BMP via file dialog | ✅ |
| Original left / Modified right, side-by-side | ✅ |
| Only the modified image responds to clicks | ✅ |
| **Remaining** counter updates immediately on each find | ✅ |
| Cumulative score across multiple rounds | ✅ |
| Red circles on **both** images for found differences | ✅ |
| Numbers inside circles (1–5) for clarity | ✅ |
| Orange ✕ flash on wrong click location | ✅ |
| Mistake counter displayed; colour-coded (grey → orange → red) | ✅ |
| Max 3 mistakes; lockout with message stating diffs found | ✅ |
| **Reveal** button — blue circles on both images | ✅ |
| Completion pop-up dialog with cumulative score | ✅ |
| Loading new image fully resets the round | ✅ |
