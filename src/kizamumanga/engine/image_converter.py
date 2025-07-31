"""ImageConverter provides image transformations such as grayscale, crop, and resize."""

import os

import cv2
from PIL import Image

from utils import Logger


class ImageConverter:
    """Applies image transformations including resize, grayscale, and content-aware crop."""

    def __init__(self, image_path: str):
        """Initialize with a path to the image to be processed."""
        self.logger = Logger("engine.image_converter")
        self.image_path = image_path
        if not os.path.exists(image_path):
            self.logger.error("Image path was not found")
            raise FileNotFoundError("Image path was not found")

    def resize(self, width, height):
        """Resize the image while preserving aspect ratio."""
        try:
            with Image.open(self.image_path) as img:
                img_ratio = img.width / img.height
                target_ratio = width / height

                if img_ratio > target_ratio:
                    height = round(width / img_ratio)
                else:
                    width = round(height * img_ratio)

                if width <= 0 or height <= 0:
                    raise ValueError(
                        f"there was an error processing the image. Width:{width}, Height:{height}")
                
                resized = img.resize((width, height), resample=Image.Resampling.LANCZOS)
                resized.save(self.image_path)

        except OSError as e:
            self.logger.exception(f"Resize failed for {self.image_path}: {e}")
            raise RuntimeError from e

    def grayscale(self):
        """Convert the image to grayscale and overwrite the original."""
        img = cv2.imread(self.image_path)
        if img is None:
            self.logger.error("Image could not be loaded for grayscale conversion")
            raise ValueError("Image could not be loaded for grayscale conversion")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(self.image_path, gray)

    def crop_countors(self, padding=10, img_is_grayscale=False):
        """Crop margins by detecting contours in the image content."""
        try:
            if img_is_grayscale:
                grey = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
                image = grey.copy()
            else:
                image = cv2.imread(self.image_path)
                grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            if image is None:
                self.logger.error("Image could not be loaded for cropping")
                return

            _, thresh = cv2.threshold(grey, 250, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                self.logger.warning(f"No contours found in {self.image_path}")
                return

            x_min, y_min, x_max, y_max = image.shape[1], image.shape[0], 0, 0
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                x_min = min(x_min, x)
                y_min = min(y_min, y)
                x_max = max(x_max, x + w)
                y_max = max(y_max, y + h)

            x_min = max(x_min - padding, 0)
            y_min = max(y_min - padding, 0)
            x_max = min(x_max + padding, image.shape[1])
            y_max = min(y_max + padding, image.shape[0])

            cropped = image[y_min:y_max, x_min:x_max]
            cv2.imwrite(self.image_path, cropped)

        except Exception as e:
            self.logger.error(f"Cropping failed for {self.image_path}: {e}")
