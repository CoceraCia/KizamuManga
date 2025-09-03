"""Downloader for manga chapters using a scraping interface and optional image processing."""

import asyncio
import os
from io import BytesIO
import ssl

import aiohttp

from scraping.interface import ScraperInterface
from scraping.base import MangaError
from utils.logger import Logger
from .image_converter import ImageConverter
from .config import Config


class MangaDownloader:
    """Handles downloading and processing manga chapter images."""

    def __init__(self, scraper: ScraperInterface, verify=True):
        """Initialize downloader with scraper and optional SSL verification."""
        self._logger = Logger("engine.downloader")
        self.scraper = scraper
        self.config = Config()

        self.ssl_context = ssl.create_default_context()
        if not verify:
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE

    async def download_chap(self, chapter_url: str, path: str) -> bool:
        """Download a chapter from URL and save images to the specified path."""
        try:
            img_dict = await self.scraper.obtain_chapter_content(chapter_url)

            if not img_dict:
                self._logger.error(f"No images found for chapter at {chapter_url}")
                raise MangaError(f"Chapter not found at {chapter_url}")

            async with aiohttp.ClientSession() as session:
                for img_name, url in img_dict.items():
                    if url.strip() == "" or url == "N/A":
                        self._logger.error(f"Invalid URL for image {img_name}")
                        raise MangaError(f"Invalid URL for image {img_name}")

                    for _ in range(5):
                        try:
                            async with session.get(
                                url,
                                ssl=self.ssl_context,
                                timeout=aiohttp.ClientTimeout(total=5),
                            ) as r:
                                content = await r.read()
                                buffer = BytesIO(content)
                                img = self.__process_image(buffer)
                                img_path = os.path.normpath(f"{path}/{img_name}.png")
                                with open(img_path, "wb") as f:
                                    f.write(img.getvalue())
                                    self._logger.info(f"Downloaded: {img_path}")
                                break
                        except asyncio.TimeoutError:
                            self._logger.error(f"Timeout while downloading {img_name}")
                        except FileNotFoundError:
                            self._logger.error("Download interrupted by user")
                        except Exception:
                            self._logger.error("Image download failed probably by antibot")
                    else:
                        self._logger.error(f"Failed after 5 retries: {img_name}")
                        return False

            self._logger.info(f"Chapter downloaded: {chapter_url} at {path}")
            return True

        except aiohttp.ClientError as e:
            self._logger.error(f"Client error during download: {e}")
            return False

    def __process_image(self, image_buffer):
        """Apply grayscale, cropping, and resizing to a downloaded image."""
        width = self.config.width
        height = self.config.height
        imgc = ImageConverter(image_buffer)
        try:
            if not self.config.color:
                imgc.grayscale()
                self._logger.info(f"Grayscale applied: {image_buffer}")

            if self.config.cropping_mode:
                is_grayscale = not self.config.color
                imgc.crop_countors(img_is_grayscale=is_grayscale)
                self._logger.info(f"Cropped: {image_buffer}")

            if width is not None and height is not None:
                imgc.resize(width=width, height=height)
                self._logger.info(f"Resized: {image_buffer}")

            return imgc.retrieve_buffered_img()

        except Exception as e:
            self._logger.error(f"Processing failed for {image_buffer}: {e}")
            raise