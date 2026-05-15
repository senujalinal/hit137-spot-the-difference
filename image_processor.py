"""
image_processor.py
HIT137 Group Assignment 3

Handles image loading and applying differences using OpenCV.

Six alteration types are implemented:
  1. ColourShiftAlteration  - hue rotation in HSV colour space
  2. BlurAlteration         - Gaussian blur patch
  3. BrightnessAlteration   - brightness +/- via convertScaleAbs
  4. SaturationAlteration   - saturation shift in HSV colour space
  5. PatchFlipAlteration    - horizontal flip of the region content
  6. NoiseAlteration        - Gaussian noise injection

_generate_differences places 5 non-overlapping alterations at random positions and types.
"""

import random
import cv2
import numpy as np

# Base class

class Alteration:
    # Base class for all image alterations.

    def __init__(self, region):
        # store the (x, y, w, h) bounding box this alteration applies to
        self._region = region

    @property
    def region(self):
        return self._region

    def apply(self, image):
        raise NotImplementedError("Subclasses must implement apply()")

    def __repr__(self):
        return f"{self.__class__.__name__}(region={self._region})"

# Alteration subclasses

class ColourShiftAlteration(Alteration):
    # Shifts the hue of a region using HSV colour space.

    def __init__(self, region, hue_shift=None):
        super().__init__(region)
        # randomise how far the hue rotates so every round looks different
        self._hue_shift = hue_shift if hue_shift is not None else random.randint(15, 40)

    def apply(self, image):
        x, y, w, h = self._region
        modified = image.copy()
        roi = modified[y:y + h, x:x + w]
        # convert to HSV so we can shift the hue channel directly
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV).astype(np.int32)
        # wrap around 180 because OpenCV hue range is 0-179
        hsv[:, :, 0] = (hsv[:, :, 0] + self._hue_shift) % 180
        modified[y:y + h, x:x + w] = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        return modified


class BlurAlteration(Alteration):
    # Applies gaussian blur to a region.

    def __init__(self, region, kernel_size=None):
        super().__init__(region)
        # larger kernel means stronger blur; must be odd for GaussianBlur
        self._kernel_size = kernel_size if kernel_size is not None else random.choice([11, 13, 15, 17])

    def apply(self, image):
        x, y, w, h = self._region
        modified = image.copy()
        # apply blur only to the patch, leaving the rest of the image untouched
        modified[y:y + h, x:x + w] = cv2.GaussianBlur(
            modified[y:y + h, x:x + w], (self._kernel_size, self._kernel_size), 0
        )
        return modified


class BrightnessAlteration(Alteration):
    # Adjusts brightness of a region using convertScaleAbs.

    def __init__(self, region, beta=None):
        super().__init__(region)
        if beta is not None:
            self._beta = beta
        else:
            mag = random.randint(30, 60)
            # randomly decide whether to lighten or darken the patch
            self._beta = mag if random.random() > 0.5 else -mag

    def apply(self, image):
        x, y, w, h = self._region
        modified = image.copy()
        # alpha=1.0 keeps contrast the same; beta shifts all pixels by a fixed amount
        modified[y:y + h, x:x + w] = cv2.convertScaleAbs(
            modified[y:y + h, x:x + w], alpha=1.0, beta=self._beta
        )
        return modified


class SaturationAlteration(Alteration):
    # Shifts the saturation channel in HSV colour space.

    def __init__(self, region, sat_shift=None):
        super().__init__(region)
        if sat_shift is not None:
            self._sat_shift = sat_shift
        else:
            mag = random.randint(40, 80)
            # positive shift makes colours more vivid; negative washes them out
            self._sat_shift = mag if random.random() > 0.5 else -mag

    def apply(self, image):
        x, y, w, h = self._region
        modified = image.copy()
        roi = modified[y:y + h, x:x + w]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV).astype(np.int32)
        # clamp to 0-255 so we don't wrap around into invalid saturation values
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] + self._sat_shift, 0, 255)
        modified[y:y + h, x:x + w] = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        return modified


class PatchFlipAlteration(Alteration):
    # Horizontally flips the content of a region using cv2.flip.

    def apply(self, image):
        x, y, w, h = self._region
        modified = image.copy()
        # flipCode=1 means horizontal flip (left becomes right)
        modified[y:y + h, x:x + w] = cv2.flip(modified[y:y + h, x:x + w], 1)
        return modified


class NoiseAlteration(Alteration):
    # Injects Gaussian noise into a region, making it appear grainy.

    def __init__(self, region, sigma=None):
        super().__init__(region)
        # higher sigma means more visible grain; kept subtle enough to be a fair challenge
        self._sigma = sigma if sigma is not None else random.uniform(22, 38)

    def apply(self, image):
        x, y, w, h = self._region
        modified = image.copy()
        # work in float so the noise addition doesn't clip before we're ready
        roi   = modified[y:y + h, x:x + w].astype(np.float32)
        noise = np.random.normal(0, self._sigma, roi.shape).astype(np.float32)
        # clip back to valid pixel range before saving as uint8
        modified[y:y + h, x:x + w] = np.clip(roi + noise, 0, 255).astype(np.uint8)
        return modified

# ImageProcessor

class ImageProcessor:
    """
    Loads images and generates 5 non-overlapping random differences.
    All image processing done using OpenCV.
    """

    # total number of hidden differences placed into the modified image
    NUM_DIFFERENCES = 5
    # smallest patch size in pixels; too small would be nearly impossible to click
    MIN_REGION_SIZE = 45
    # largest patch size; keeps differences from taking up too much of the image
    MAX_REGION_SIZE = 110
    # gap between difference regions and the image edge
    MARGIN = 15
    # how many random positions to try before giving up on placing a region
    MAX_ATTEMPTS = 500

    SUPPORTED_FORMATS = (
        ("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
        ("JPEG", "*.jpg *.jpeg"),
        ("PNG", "*.png"),
        ("BMP", "*.bmp"),
        ("All Files", "*.*"),
    )

    # all available alteration types the game can randomly choose from
    _ALTERATION_TYPES = [
        ColourShiftAlteration,
        BlurAlteration,
        BrightnessAlteration,
        SaturationAlteration,
        PatchFlipAlteration,
        NoiseAlteration,
    ]

    def __init__(self):
        self._original_bgr = None
        self._modified_bgr = None
        self._alterations = []

    def load_image(self, path):
        # Load image from disk and generate differences.
        img = cv2.imread(path)
        # imread returns None if the file can't be read or isn't a valid image
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
        # Clone image and inject exactly 5 non-overlapping alterations.
        img_h, img_w = image.shape[:2]
        placed = []
        alterations = []
        modified = image.copy()

        # sample without replacement so every difference looks different this round
        type_pool = random.sample(self._ALTERATION_TYPES, self.NUM_DIFFERENCES)

        for i in range(self.NUM_DIFFERENCES):
            region = self._find_region(img_w, img_h, placed)
            # skip this slot if no valid position could be found after MAX_ATTEMPTS tries
            if region is None:
                continue
            alt = type_pool[i](region)
            placed.append(region)
            alterations.append(alt)
            # apply each alteration on top of the previous ones, building up the modified image
            modified = alt.apply(modified)

        return modified, alterations

    def _find_region(self, img_w, img_h, existing):
        # Find a random non-overlapping region.
        rw = random.randint(self.MIN_REGION_SIZE, self.MAX_REGION_SIZE)
        rh = random.randint(self.MIN_REGION_SIZE, self.MAX_REGION_SIZE)

        x_min = self.MARGIN
        x_max = img_w - rw - self.MARGIN
        y_min = self.MARGIN
        y_max = img_h - rh - self.MARGIN

        # image is too small to fit even one region with the required margins
        if x_max <= x_min or y_max <= y_min:
            return None

        for _ in range(self.MAX_ATTEMPTS):
            x = random.randint(x_min, x_max)
            y = random.randint(y_min, y_max)
            candidate = (x, y, rw, rh)
            # only accept this position if it doesn't collide with any already placed region
            if not any(self._overlaps(candidate, ex) for ex in existing):
                return candidate
        return None

    @staticmethod
    def _overlaps(a, b, pad=15):
        #Check if two regions overlap with padding buffer.
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        # pad adds a small gap between regions so they don't look like one big difference
        return not (ax + aw + pad <= bx or bx + bw + pad <= ax
                    or ay + ah + pad <= by or by + bh + pad <= ay)