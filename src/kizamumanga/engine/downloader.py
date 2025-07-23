"""MangaDownloader class to handle downloading manga chapters.
This class uses the ScraperInterface to obtain chapter content and download images."""
import asyncio
import aiohttp
from scraping.interface import ScraperInterface
from scraping.base import MangaError
from .logger import Logger


class MangaDownloader:
    """MangaDownloader class to handle downloading manga chapters."""
    def __init__(self, scraper:ScraperInterface):
        self._logger = Logger("engine.downloader")
        self.scraper = scraper

    async def download_chap(self, chapter_url:str, path:str) -> bool:
        """Download a chapter from the given URL and save it to the specified path."""
        try:
            img_dict = await self.scraper.obtain_chapter_content(chapter_url)

            if img_dict == {}:
                self._logger.error(f"No images found for chapter at {chapter_url}")
                raise MangaError(f"Chapter not found at {chapter_url}")
            for img_name, url in img_dict.items():
                async with aiohttp.ClientSession() as session:
                    if url.strip() == "" or url == "N/A":
                        self._logger.error(f"Invalid URL for image {img_name} in chapter {chapter_url}")
                        raise MangaError(f"Invalid URL for image {img_name} in chapter {chapter_url}")
                    while True:
                        try:
                            async with session.get(
                                url, timeout=aiohttp.ClientTimeout(total=5)
                            ) as r:
                                content = await r.read()
                                with open(
                                    f'{path}/{img_name}.png', "wb"
                                ) as f:
                                    f.write(content)
                                break
                        except asyncio.TimeoutError:
                            self._logger.error(f"TimeoutError while downloading {img_name} from {url}")
                        except (FileNotFoundError):
                            self._logger.error("Download interrupted by user")
            self._logger.info(f"Chapter downloaded successfully: {chapter_url}")
            return True
        except aiohttp.ClientError as e:
            self._logger.error(f"ClientError during download: {e}")
            return False
