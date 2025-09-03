"""ImageConverter provides image transformations such as grayscale, crop, and resize."""
from io import BytesIO
import numpy as np
import cv2
from PIL import Image

from utils import Logger


class ImageConverter:
    """Applies image transformations including resize, grayscale, and content-aware crop."""

    def __init__(self, img_buffer):
        """Initialize with a path to the image to be processed."""
        self.logger = Logger("engine.image_converter")
        self.b_img = Image.open(img_buffer)
        self.output_buffer = BytesIO()

    def resize(self, width, height):
        """Resize the image while preserving aspect ratio."""
        try:
            img = self.b_img
            img_ratio = img.width / img.height
            target_ratio = width / height

            if img_ratio > target_ratio:
                height = round(width / img_ratio)
            else:
                width = round(height * img_ratio)

            if width <= 0 or height <= 0:
                raise ValueError(
                    f"there was an error processing the image. Width:{width}, Height:{height}")
            
            self.b_img = img.resize((width, height), resample=Image.Resampling.LANCZOS)

        except OSError as e:
            self.logger.exception(f"Resize failed for {self.b_img}: {e}")
            raise RuntimeError from e

    def grayscale(self):
        """Convert the image to grayscale and overwrite the original."""
        try:
            img = np.array(self.b_img)
        except OSError as e:
            self.logger.exception(f"Resize failed for {self.b_img}: {e}")
            raise RuntimeError from e
        
        if img is None:
            self.logger.error("Image could not be loaded for grayscale conversion")
            raise ValueError("Image could not be loaded for grayscale conversion")

        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        self.b_img = Image.fromarray(gray)

    def crop_countors(self, padding=10, img_is_grayscale=False):
        """Crop margins by detecting contours in the image content."""
        try:
            image = np.array(self.b_img)

            if image is None:
                self.logger.error("Image could not be loaded for cropping")
                return

            if img_is_grayscale:
                grey = image.copy()
            else:
                grey = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            _, thresh = cv2.threshold(grey, 250, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                self.logger.warning(f"No contours found")
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
            self.b_img = Image.fromarray(cropped)
        except Exception as e:
            self.logger.error(f"Cropping failed: {e}")

    def retrieve_buffered_img(self):
        self.b_img.save(self.output_buffer, format="PNG")
        return self.output_buffer
