import os
import cv2  # Ensure opencv-python is installed: pip install opencv-python
from PIL import Image
from utils import Logger


class ImageConverter():
    def __init__(self, image_path: str):
        self.logger = Logger("engine.image_converter")
        self.image_path = image_path
        if not os.path.exists(image_path):
            self.logger.error("Image path was not found")
            raise FileNotFoundError("Image path was not found")

    def resize(self, width, height):
        """
        Resize the image while preserving its aspect ratio.
        """
        try:
            with Image.open(self.image_path) as img:
                img_ratio = img.width / img.height
                target_ratio = width / height

                # Image is wider than the target ratio
                if img_ratio > target_ratio:
                    height = round(width / img_ratio)
                # Image is taller than the target ratio
                else:
                    width = round(height * img_ratio)

                resized = img.resize(
                    (width, height), resample=Image.Resampling.LANCZOS)
                
                resized.save(self.image_path)
        except OSError as e:
            self.logger.exception(f"{resized.width}-{resized.height}:{e}")
            raise RuntimeError from e
    def grayscale(self):
        """
        Convert the image to grayscale and overwrite the original file.
        """
        img = cv2.imread(self.image_path)
        if img is None:
            self.logger.error("Image could not be loaded for grayscale conversion")
            raise ValueError("Image could not be loaded for grayscale conversion")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(self.image_path, gray)

    def crop_countors(self, padding=10, img_is_grayscale=False):
        """
        Crop the image by detecting content contours, removing uniform margins.
        Optionally converts to grayscale to improve contour detection.

        Args:
            padding (int): Extra margin to retain around detected content.
            grayscale (bool): Whether to convert the image to grayscale before processing.
        """
        try:
            # In case that the image was not previously converted to grayscale, set it to True
            if img_is_grayscale:
                print("is grayscale")
                grey = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
                image = grey.copy()
            else:
                image = cv2.imread(self.image_path)
                grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
            if image is None:
                self.logger.error("Image could not be loaded for cropping")
                return

            # Apply inverted binary threshold:
            _, thresh = cv2.threshold(grey, 250, 255, cv2.THRESH_BINARY_INV)

            # Detect white regions (content) as contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                return

            # Initialize crop box coordinates
            x_min, y_min, x_max, y_max = image.shape[1], image.shape[0], 0, 0

            # Expand the crop box to include all contours
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                x_min = min(x_min, x)
                y_min = min(y_min, y)
                x_max = max(x_max, x + w)
                y_max = max(y_max, y + h)

            # Apply padding, making sure not to exceed image boundaries
            x_min = max(x_min - padding, 0)
            y_min = max(y_min - padding, 0)
            x_max = min(x_max + padding, image.shape[1])
            y_max = min(y_max + padding, image.shape[0])

            # Crop the image using the computed bounding box
            cropped = image[y_min:y_max, x_min:x_max]

            # Save the cropped image, replacing the original file
            cv2.imwrite(self.image_path, cropped)
        except Exception as e:
            self.logger.error(e)