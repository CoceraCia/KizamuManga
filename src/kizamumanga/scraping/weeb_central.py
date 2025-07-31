from bs4 import BeautifulSoup

from playwright.async_api import Error, TimeoutError as PlaywrightTimeoutError

from utils.logger import Logger
from utils.general_tools import extract_num
from .interface import ScraperInterface
from .base import ScraperBase, MangaError

BASE_URL = "https://weebcentral.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36"
}


class WeebCentral(ScraperBase, ScraperInterface):
    """Scraper for WeebCentral site to fetch manga info and images."""

    def __init__(self):
        """Initialize WeebCentral scraper with logging."""
        super().__init__()
        self.logger = Logger("scraping.weeb_central")


    async def get_mangas_by_title(self, title: str) -> dict:
        """Search manga by title and return matches as {name: URL}."""
        title = title.replace(" ", "+")
        url = f"{BASE_URL}/search?text={title}&sort=Best+Match&order=Descending&official=Any&anime=Any&adult=Any&display_mode=Full+Display"
        async with await self.context.new_page() as page:
            try:
                await page.goto(url)
                await page.wait_for_selector(
                    "#search-results > article:nth-child(1)", timeout=1500
                )
                html = await page.content()
            except Error as e:
                raise MangaError("Manga not found") from e

        soup = BeautifulSoup(html, "html.parser")
        manga_names = soup.select("a.line-clamp-1")

        nl = {}
        for item in manga_names:
            nl[item.text.strip()] = item.get("href", "N/A")

        return nl

    async def get_chapters_by_mangaurl(self, manga_url) -> dict:
        """Return chapters for a manga as {chapter_name: URL}, sorted by chapter number."""
        async with await self.context.new_page() as page:
            await page.goto(manga_url)
            element = await page.query_selector("#chapter-list > button")
            if element:
                await page.wait_for_selector("#chapter-list > button")
                await page.click("#chapter-list > button")
                await page.wait_for_timeout(1200)
            html = await page.content()

        soup = BeautifulSoup(html, "html.parser")
        tags = soup.find_all(
            "a", class_="hover:bg-base-300 flex-1 flex items-center p-2"
        )
        # Retrieveng mangas
        nl = {}
        for tag in tags:
            href = tag.get("href", "N/A")
            for span in tag.find_all("span"):
                if span.has_attr("class") and span["class"] == []:
                    nl[span.text.strip()] = href.strip()
                    break

        # Sorting the retrieved mangas
        sorted_nl = {}
        for chap in sorted(nl, key=extract_num):
            sorted_nl[chap] = nl[chap]

        return sorted_nl
                            

    async def obtain_chapter_content(self, manga_url) -> dict:
        """Get image URLs for a chapter as {image_name: src}."""
        while True:
            try:
                async with await self.context.new_page() as page:
                    await page.goto(manga_url)

                    await page.wait_for_timeout(2000)
                    await page.wait_for_selector("img[alt *= 'Page']", timeout=5000)
                    html = await page.content()
                    break
            except PlaywrightTimeoutError:
                pass

        soup = BeautifulSoup(html, "html.parser")
        tags = soup.find_all("img")

        chapters_dict = {}

        for tag in tags:
            if tag.has_attr("alt") and "Page" in tag["alt"]:
                chapters_dict[tag["alt"]] = tag.get("src", "N/A")

        return chapters_dict
