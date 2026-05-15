# HIT137 - Group Assignment 3: Spot the Difference

A fully-featured desktop "Spot the Difference" game built with **Python 3**, **Tkinter**, and **OpenCV**, satisfying all requirements of HIT137 Group Assignment 3.

---

## Quick Start

### Windows

**1. Install dependencies**
```bash
pip install opencv-python pillow numpy
```

**2. Generate the built-in sample image (optional)**
```bash
python sample_generator.py
```

This creates `sample_image.png` - a colourful geometric scene you can load immediately without sourcing your own photograph.

**3. Launch the game**
```bash
python main.py
```

---

### macOS

**1. Install dependencies**
```bash
pip3 install opencv-python pillow numpy
```

> Tkinter is not bundled with Homebrew Python. If you see a Tkinter import error, run:
> ```bash
> brew install python-tk
> ```

**2. Generate the built-in sample image (optional)**
```bash
python3 sample_generator.py
```

**3. Launch the game**
```bash
python3 main.py
```

---


## How to Play

| Step | Action |
|------|--------|
| 1 | Click **Load Image** and choose any JPG, PNG, BMP, or TIFF file |
| 2 | The **Original** image appears on the left (reference only) |
| 3 | Click the **Modified** image on the right to locate differences |
| 4 | A **red circle** appears on **both** images when you find one |
| 5 | Find all **5** differences to complete the round |
| 6 | You have **3 incorrect clicks** before the round locks out |
| 7 | Press **Reveal All** at any time to show remaining differences in **blue** |
| 8 | Load a new image to keep playing - your score is cumulative |

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
Alteration  (abstract base - inheritance, polymorphism)
├── ColourShiftAlteration   hue rotation in HSV colour space
├── BlurAlteration          Gaussian blur (cv2.GaussianBlur)
├── BrightnessAlteration    brightness delta (cv2.convertScaleAbs)
├── SaturationAlteration    saturation shift in HSV colour space
├── PatchFlipAlteration     horizontal flip (cv2.flip)
└── NoiseAlteration         Gaussian noise injection

tk.Canvas  (Tkinter built-in)
└── ImageCanvas             display and overlay drawing (inheritance)

ImageProcessor              image I/O and difference orchestration
GameState                   click detection, mistakes, cumulative score
GameWindow                  GUI shell; composes ImageProcessor + GameState
```

### OOP Principles

| Principle | Implementation |
|-----------|---------------|
| **Encapsulation** | All state is `_private`; exposed read-only via `@property` |
| **Inheritance** | `ImageCanvas` extends `tk.Canvas`; six alteration types extend `Alteration` |
| **Polymorphism** | `alteration.apply(img)` called uniformly regardless of concrete subtype |
| **Constructors** | Every class has `__init__` with documented parameters |
| **Class interaction** | `GameWindow` drives `ImageProcessor` and `GameState`; they do not know about each other |
| **3 or more classes** | 11 distinct classes across 4 modules |

---

## Image Processing (OpenCV)

All pixel-level work uses **OpenCV** and **NumPy**:

| Alteration | OpenCV technique |
|------------|-----------------|
| Colour Shift | `cv2.cvtColor` (BGR to HSV), hue channel rotation |
| Blur | `cv2.GaussianBlur` with random odd kernel (11-17) |
| Brightness | `cv2.convertScaleAbs(alpha=1.0, beta=+/-30-60)` |
| Saturation | `cv2.cvtColor` (BGR to HSV), saturation channel clamp-shift |
| Patch Flip | `cv2.flip` with horizontal flip code |
| Noise | `numpy.random.normal` added to float patch, clipped back to uint8 |

**Non-overlap guarantee:** rejection sampling with AABB separation testing and 15 px padding ensures all 5 regions are visually distinct every load.

**No-repeat guarantee:** `random.sample` selects 5 unique types from the 6 available each round, so no alteration type appears twice in the same image.

---

## Gameplay Features (Tkinter GUI)

| Requirement | Status |
|-------------|--------|
| Load image - JPG, PNG, BMP, TIFF via file dialog | Met |
| Original left / Modified right, side-by-side | Met |
| Only the modified image responds to clicks | Met |
| Remaining counter updates immediately on each find | Met |
| Cumulative score across multiple rounds | Met |
| Red circles on both images for found differences | Met |
| Numbers inside circles (1-5) for order clarity | Met |
| Orange cross flash on wrong click location | Met |
| Mistake counter displayed; colour-coded (grey, orange, red) | Met |
| Max 3 mistakes per image; lockout with message stating diffs found | Met |
| Reveal button - blue circles on both images for unfound differences | Met |
| Completion pop-up dialog with cumulative score | Met |
| Loading new image fully resets the round | Met |
