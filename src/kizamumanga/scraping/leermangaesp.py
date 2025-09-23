from bs4 import BeautifulSoup

from playwright.async_api import Error, TimeoutError as PlaywrightTimeoutError, Page

from tenacity import retry, stop_after_attempt, wait_exponential

from utils.logger import Logger
from utils.general_tools import extract_num
from .interface import ScraperInterface
from .base import ScraperBase, MangaError

BASE_URL = "https://leermangaesp.com/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36"
}


class LeerMangaEsp(ScraperBase, ScraperInterface):
    """Scraper for leermangaesp site to fetch manga info and images."""

    def __init__(self):
        """Initialize leermangaesp scraper with logging."""
        super().__init__()
        self.logger = Logger("scraping.weeb_central")

    @staticmethod
    def __retry_state(retry_state):
        last_outcome = getattr(retry_state, "outcome", None)
        err = last_outcome.exception() if last_outcome and last_outcome.failed else None
        raise MangaError(
            f"Retries exhausted after {retry_state.attempt_number} attempts") from err

    _RETRY_KW = dict(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=0.5, max=4),
        retry_error_callback=__retry_state.__func__,
    )

    async def __close_page(self, page: Page):
        if page:
            try:
                await page.close()
            except Exception:
                pass

    @retry(**_RETRY_KW)
    async def get_mangas_by_title(self, title: str) -> dict:
        """Search manga by title and return matches as {name: URL}."""
        page = None
        url = BASE_URL
        try:
            page = await self.context.new_page()
            await page.set_extra_http_headers(HEADERS)
            await page.goto(url, wait_until="domcontentloaded", timeout=10000)
            await page.wait_for_selector("#searchInput", timeout=1000)
            await page.fill("#searchInput", title)
            await page.press("#searchInput", "Enter")
            await page.wait_for_selector(".manga-item", state="visible", timeout=1000)
            
            html = await page.content()
        except Error as e:
            raise MangaError("Manga not found") from e
        finally:
            await self.__close_page(page)

        soup = BeautifulSoup(html, "html.parser")
        mangas = soup.select(".manga-item")

        nl = {}
        for item in mangas:
            title = item.find("h3").text
            url = BASE_URL + item.find("a").get("href")
            nl[title] = url.replace("//", "/")

        return nl

    @retry(**_RETRY_KW)
    async def get_chapters_by_mangaurl(self, manga_url) -> dict:
        """Return chapters for a manga as {chapter_name: URL}, sorted by chapter number."""
        page = None
        try:
            page = await self.context.new_page()
            await page.set_extra_http_headers(HEADERS)
            await page.goto(manga_url, wait_until="domcontentloaded")
            
            await page.wait_for_selector(".chapter-card", state="visible", timeout=1000)
            
            html = await page.content()

            soup = BeautifulSoup(html, "html.parser")
            
            chapters = soup.select(".chapter-link")
            
            # Retrieveng mangas
            nl = {}
            for item in chapters:
                url = item.get("href")
                title = item.get("aria-label")
                nl[title] = (BASE_URL + url).replace("//", "/")

            # Sorting the retrieved mangas
            sorted_nl = {}
            for chap in sorted(nl, key=extract_num):
                sorted_nl[chap] = nl[chap]

            return sorted_nl
        finally:
            await self.__close_page(page)

    @retry(**_RETRY_KW)
    async def obtain_chapter_content(self, manga_url) -> dict:
        """Get image URLs for a chapter as {image_name: src}."""
        page = None
        try:
            page = await self.context.new_page()
            await page.set_extra_http_headers(HEADERS)

            await page.goto(manga_url, wait_until="domcontentloaded")

            await page.wait_for_selector(".manga-image", timeout=2000)
            
            html = await page.content()
        except PlaywrightTimeoutError:
            raise
        finally:
            await self.__close_page(page)

        soup = BeautifulSoup(html, "html.parser")
        imgs = soup.select("#cascade-view img")
        chapters_dict = {}
        
        for item in imgs:
            alt = item.get("alt")
            src = item.get("src")
            chapters_dict[alt] = src

        return chapters_dict
