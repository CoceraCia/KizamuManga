import asyncio
import aiohttp
from scraping import ScraperInterface


class MangaDownloader:
    def __init__(self, scraper:ScraperInterface):
        self.scraper = scraper
    async def download_chap(self, chapter_url:str, path:str):
        img_dict = await self.scraper.obtain_chapter_content(chapter_url)
        for img_name, url in img_dict.items():
            async with aiohttp.ClientSession() as session:
                if url.strip() == "":
                    print("no data")
                if url == "N/A":
                    print("No image found")
                    break
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
                        print("TimeoutError")