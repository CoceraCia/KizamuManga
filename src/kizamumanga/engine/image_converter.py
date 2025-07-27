import os
import cv2  # Make sure opencv-python is installed: pip install opencv-python
from PIL import Image
from utils import Logger


class ImageConverter():
    def __init__(self, image_path: str):
        self.logger = Logger("engine.image_converter")
        self.image_path = image_path
        if not os.path.exists(image_path):
            self.logger.error("image path wasn't found")
            raise FileNotFoundError("image path wasn't found")

    async def resize(self, width, height):
        with Image.open(self.image_path) as img:
            img_ratio = img.width / img.height
            target_ratio = width / height

            # img wider than ratio
            if img_ratio > target_ratio:
                height = round(width / img_ratio)
            # img higher than ratio
            else:
                width = round(height * img_ratio)

            resized = img.resize(
                (width, height), resample=Image.Resampling.LANCZOS)
            resized.save(self.image_path)

    async def grayscale(self):
        img = cv2.imread(self.image_path)
        if img is None:
            self.logger.error("Image couldn't load to apply grayscale")
            raise ValueError("Image couldn't load to apply grayscale")

        # Conversión simple a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Guardar imagen en escala de grises
        cv2.imwrite(self.image_path, gray)
