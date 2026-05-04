"""
image_processor.py
HIT137 Group Assignment 3

Handles image loading and applying differences using OpenCV.
"""

import random
import cv2
import numpy as np


class Alteration:
    """Base class for all image alterations."""

    def __init__(self, region):
        self._region = region

    @property
    def region(self):
        return self._region

    def apply(self, image):
        raise NotImplementedError("Subclasses must implement apply()")

    def __repr__(self):
        return f"{self.__class__.__name__}(region={self._region})"


class ColourShiftAlteration(Alteration):
    """Shifts the hue of a region using HSV colour space."""

    def __init__(self, region, hue_shift=None):
        super().__init__(region)
        self._hue_shift = hue_shift if hue_shift is not None else random.randint(15, 40)

    def apply(self, image):
        x, y, w, h = self._region
        modified = image.copy()
        roi = modified[y:y + h, x:x + w]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV).astype(np.int32)
        hsv[:, :, 0] = (hsv[:, :, 0] + self._hue_shift) % 180
        modified[y:y + h, x:x + w] = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        return modified


class BlurAlteration(Alteration):
    """Applies gaussian blur to a region."""

    def __init__(self, region, kernel_size=None):
        super().__init__(region)
        self._kernel_size = kernel_size if kernel_size is not None else random.choice([11, 13, 15, 17])

    def apply(self, image):
        x, y, w, h = self._region
        modified = image.copy()
        modified[y:y + h, x:x + w] = cv2.GaussianBlur(
            modified[y:y + h, x:x + w], (self._kernel_size, self._kernel_size), 0
        )
        return modified


class BrightnessAlteration(Alteration):
    """Adjusts brightness of a region using convertScaleAbs."""

    def __init__(self, region, beta=None):
        super().__init__(region)
        if beta is not None:
            self._beta = beta
        else:
            mag = random.randint(30, 60)
            self._beta = mag if random.random() > 0.5 else -mag

    def apply(self, image):
        x, y, w, h = self._region
        modified = image.copy()
        modified[y:y + h, x:x + w] = cv2.convertScaleAbs(
            modified[y:y + h, x:x + w], alpha=1.0, beta=self._beta
        )
        return modified


class SaturationAlteration(Alteration):
    """Shifts the saturation channel in HSV colour space."""

    def __init__(self, region, sat_shift=None):
        super().__init__(region)
        if sat_shift is not None:
            self._sat_shift = sat_shift
        else:
            mag = random.randint(40, 80)
            self._sat_shift = mag if random.random() > 0.5 else -mag

    def apply(self, image):
        x, y, w, h = self._region
        modified = image.copy()
        roi = modified[y:y + h, x:x + w]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV).astype(np.int32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] + self._sat_shift, 0, 255)
        modified[y:y + h, x:x + w] = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        return modified


class ImageProcessor:
    """
    Loads images and generates 5 non-overlapping random differences.
    All image processing done using OpenCV.
    """

    NUM_DIFFERENCES = 5
    MIN_REGION_SIZE = 45
    MAX_REGION_SIZE = 110
    MARGIN = 15
    OVERLAP_PADDING = 15
    MAX_ATTEMPTS = 500

    SUPPORTED_FORMATS = (
        ("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
        ("JPEG", "*.jpg *.jpeg"),
        ("PNG", "*.png"),
        ("BMP", "*.bmp"),
        ("All Files", "*.*"),
    )

    _ALTERATION_TYPES = [
        ColourShiftAlteration,
        BlurAlteration,
        BrightnessAlteration,
        SaturationAlteration,
    ]

    def __init__(self):
        self._original_bgr = None
        self._modified_bgr = None
        self._alterations = []

    def load_image(self, path):
        """Load image from disk and generate differences."""
        img = cv2.imread(path)
        if img is None:
            return False
        self._original_bgr = img
        self._modified_bgr, self._alterations = self._generate_differences(img)
        return True

    @property
    def original_bgr(self):
        return self._original_bgr

    @property
    def modified_bgr(self):
        return self._modified_bgr

    @property
    def alterations(self):
        return list(self._alterations)

    @property
    def image_size(self):
        if self._original_bgr is None:
            return None
        h, w = self._original_bgr.shape[:2]
        return w, h

    def _generate_differences(self, image):
        """Clone image and inject exactly 5 non-overlapping alterations."""
        img_h, img_w = image.shape[:2]
        placed = []
        alterations = []
        modified = image.copy()

        for i in range(self.NUM_DIFFERENCES):
            region = self._find_region(img_w, img_h, placed)
            if region is None:
                print(f"Warning: could not place difference {i+1}")
                continue
            placed.append(region)
            cls = random.choice(self._ALTERATION_TYPES)
            alt = cls(region)
            alterations.append(alt)
            modified = alt.apply(modified)

        return modified, alterations

    def _find_region(self, img_w, img_h, existing):
        """Find a random non-overlapping region."""
        rw = random.randint(self.MIN_REGION_SIZE, self.MAX_REGION_SIZE)
        rh = random.randint(self.MIN_REGION_SIZE, self.MAX_REGION_SIZE)

        x_min = self.MARGIN
        x_max = img_w - rw - self.MARGIN
        y_min = self.MARGIN
        y_max = img_h - rh - self.MARGIN

        if x_max <= x_min or y_max <= y_min:
            return None

        for _ in range(self.MAX_ATTEMPTS):
            x = random.randint(x_min, x_max)
            y = random.randint(y_min, y_max)
            candidate = (x, y, rw, rh)
            if not any(self._overlaps(candidate, ex) for ex in existing):
                return candidate
        return None

    @staticmethod
    def _overlaps(a, b, pad=15):
        """Check if two regions overlap with padding buffer."""
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return not (ax + aw + pad <= bx or bx + bw + pad <= ax
                    or ay + ah + pad <= by or by + bh + pad <= ay)
