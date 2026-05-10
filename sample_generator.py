"""
sample_generator.py
===================
Generates a rich, colourful sample image that can be used to test the
Spot the Difference game without needing an external photograph.

The generated image is saved as ``sample_image.png`` in the same directory.
It can be opened directly from the game's Load Image dialog.

Usage
-----
    python3.13 sample_generator.py

All image construction is performed using OpenCV (``cv2``) as required by
the assignment specification.

Author : HIT137 Group Assignment 3
"""

import os
import cv2
import numpy as np


def generate_sample_image(
    output_path: str = "sample_image.png",
    width: int = 800,
    height: int = 600,
) -> str:
    """
    Create a colourful geometric scene using OpenCV drawing primitives
    and save it to *output_path*.

    The image deliberately contains multiple coloured shapes, gradients,
    and textures so that the four alteration types (hue shift, blur,
    brightness, saturation) are clearly visible when applied.

    Parameters
    ----------
    output_path : str
        File path for the saved image (PNG format).
    width, height : int
        Dimensions of the generated image in pixels.

    Returns
    -------
    str
        Absolute path to the saved image file.
    """
    # ── Base gradient background (top-to-bottom: deep blue → teal) ────
    img = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        t = y / height
        r = int(15  + (30  - 15)  * t)
        g = int(30  + (120 - 30)  * t)
        b = int(100 + (150 - 100) * t)
        img[y, :] = (b, g, r)  # OpenCV is BGR

    # ── Large background shapes ────────────────────────────────────────

    # Sky ellipse (light cyan)
    cv2.ellipse(img, (width // 2, 80), (300, 120), 0, 0, 180, (200, 230, 255), -1)

    # Ground rectangle (earthy green)
    cv2.rectangle(img, (0, height - 140), (width, height), (40, 120, 60), -1)

    # ── Coloured geometric shapes (give difference regions colour variety) ──

    # Red barn / house shape
    pts = np.array([
        [100, 380], [200, 280], [300, 380],
    ], np.int32)
    cv2.fillPoly(img, [pts], (50, 60, 200))          # red roof
    cv2.rectangle(img, (120, 380), (280, 460), (70, 80, 160), -1)  # walls

    # Yellow sun
    cv2.circle(img, (680, 90), 60, (30, 210, 240), -1)
    for angle in range(0, 360, 30):
        import math
        ax = int(680 + 75 * math.cos(math.radians(angle)))
        ay = int(90  + 75 * math.sin(math.radians(angle)))
        bx = int(680 + 95 * math.cos(math.radians(angle)))
        by = int(90  + 95 * math.sin(math.radians(angle)))
        cv2.line(img, (ax, ay), (bx, by), (30, 210, 240), 3)

    # Green tree trunks + canopy
    for tx, ty in [(450, 420), (530, 400), (610, 410)]:
        cv2.rectangle(img, (tx - 8, ty), (tx + 8, ty + 80), (40, 80, 100), -1)
        cv2.circle(img, (tx, ty), 45, (30, 160, 50), -1)

    # Blue pond
    cv2.ellipse(img, (180, 510), (130, 50), 0, 0, 360, (180, 140, 40), -1)
    cv2.ellipse(img, (180, 510), (130, 50), 0, 0, 360, (200, 160, 60), 2)

    # Purple mountain range
    mountain_pts = np.array([
        [350, 460], [430, 310], [510, 460],
        [480, 460], [560, 340], [640, 460],
    ], np.int32)
    cv2.fillPoly(img, [mountain_pts], (130, 70, 100))

    # Orange hot-air balloon
    cv2.circle(img, (620, 220), 70, (0, 120, 240), -1)   # balloon body
    cv2.ellipse(img, (620, 220), (70, 50), 0, 0, 360, (0, 80, 200), 3)
    cv2.rectangle(img, (605, 285), (635, 315), (60, 100, 140), -1)  # basket
    # Balloon stripes
    for stripe_x in range(560, 681, 20):
        cv2.line(img, (stripe_x, 155), (620, 290), (20, 60, 180), 2)

    # White clouds
    for cx, cy in [(120, 150), (350, 120), (540, 160)]:
        cv2.ellipse(img, (cx, cy), (70, 30), 0, 0, 360, (240, 240, 245), -1)
        cv2.ellipse(img, (cx - 30, cy + 10), (40, 25), 0, 0, 360, (240, 240, 245), -1)
        cv2.ellipse(img, (cx + 30, cy + 10), (40, 25), 0, 0, 360, (240, 240, 245), -1)

    # Colourful flowers on the ground
    flower_colours = [
        (40, 40, 240),   # red
        (40, 200, 240),  # yellow
        (200, 40, 200),  # purple-ish
        (40, 200, 100),  # green-yellow
    ]
    for i, (fx, fy) in enumerate([(50, 490), (340, 500), (720, 480), (760, 510)]):
        col = flower_colours[i % len(flower_colours)]
        cv2.circle(img, (fx, fy), 14, col, -1)
        cv2.circle(img, (fx, fy), 6, (255, 255, 255), -1)

    # Apply subtle overall Gaussian blur for a polished look
    img = cv2.GaussianBlur(img, (3, 3), 0)

    # ── Save ───────────────────────────────────────────────────────────
    abs_path = os.path.abspath(output_path)
    cv2.imwrite(abs_path, img)
    print(f"Sample image saved to: {abs_path}")
    return abs_path


if __name__ == "__main__":
    generate_sample_image()
