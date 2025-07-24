from PIL import Image
from PIL.Image import Resampling
class ImageConverter():
    def __init__(self, image_path:str):
        self.image_path = image_path

    async def resize(self, width,height):
        with Image.open(self.image_path) as img:
            img_ratio = img.width / img.height
            target_ratio = width / height

            # img wider than ratio
            if img_ratio > target_ratio:
                height = round(width / img_ratio)
            # img higher than ratio
            else:
                width = round(height * img_ratio)

            resized = img.resize((width, height), resample = Resampling.LANCZOS)
            resized.save(self.image_path)
