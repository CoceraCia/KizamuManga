from bs4 import BeautifulSoup

from playwright.async_api import Error, TimeoutError as PlaywrightTimeoutError, Page

from tenacity import retry, stop_after_attempt, wait_exponential

from utils.logger import Logger
from utils.general_tools import extract_num
from .interface import ScraperInterface
from .base import ScraperBase, MangaError

import time

BASE_URL = "https://inmanga.com/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36"
}


class InManga(ScraperBase, ScraperInterface):
    """Scraper for WeebCentral site to fetch manga info and images."""

    def __init__(self):
        """Initialize WeebCentral scraper with logging."""
        super().__init__()
        self.logger = Logger("scraping.inmanga")

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
        url = f"{BASE_URL}manga/consult"
        try:
            page = await self.context.new_page()
            await page.set_extra_http_headers(HEADERS)
            await page.goto(url, wait_until="domcontentloaded", timeout=3000)
            time.sleep(2)
            await page.type("#SearchManga", title, delay=100, timeout=3000)
            time.sleep(1)
            try:
                await page.wait_for_selector("#MangaConsultResult > a:nth-child(2)", timeout=1000)
            except Error as e:
                print("Manga not found")
                return
            html = await page.content()
        except Error as e:
            raise MangaError("Manga not found") from e
        finally:
            await self.__close_page(page)

        soup = BeautifulSoup(html, "html.parser")
        manga_names = soup.select("a.manga-result")

        nl = {}
        for i,item in enumerate(manga_names, start=0):
            names = soup.select("img.lazy")
            name = names[i].get("alt", "N/A").replace("Manga Online - InManga", "").strip()
            nl[name] = f"{BASE_URL}{item.get("href", "N/A")}"
        if nl is not None:
            print("found")
            return nl
        else:
            print("not found")
            return

    @retry(**_RETRY_KW)
    async def get_chapters_by_mangaurl(self, manga_url) -> dict:
        """Return chapters for a manga as {chapter_name: URL}, sorted by chapter number."""
        page = None
        try:
            page = await self.context.new_page()
            await page.set_extra_http_headers(HEADERS)
            await page.goto(manga_url, wait_until="domcontentloaded")
            await page.wait_for_selector("#ChaptersContainer > a:nth-child(2)", timeout=2000)
            html = await page.content()

            soup = BeautifulSoup(html, "html.parser")

            chaps = soup.select("a.viewed-chapter")

            # Retrieving mangas
            nl = {}
            for chap in chaps:
                href = chap.get("href")
                nl[f"Capitulo: {chap.get("data-c-number")}"] = href

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
        manga_url = BASE_URL + manga_url
        try:
            page = await self.context.new_page()
            await page.set_extra_http_headers(HEADERS)

            await page.goto(manga_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            await page.wait_for_selector("a.NextPage:nth-child(1)")
            
            while True:
                height1 = await page.evaluate("document.scrollingElement.scrollHeight")
                for i in range(round(height1/200) + 50):
                    await page.mouse.wheel(0,200)
                height2 = await page.evaluate("document.scrollingElement.scrollHeight")
                if height1 == height2:
                    break
            i = 0
            while True:
                if i != 2:
                    html = await page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    tags = soup.select("img.ImageContainer")
                    
                    loaded = True
                    for tag in tags:
                        if ".gif" in tag.get("src"):
                            loaded = False
                            print("Not charged")
                            break
                    if loaded:
                        break
                    i += 1
                    time.sleep(1)
                else:
                    print("Couldn't load all imgs")
                    raise PlaywrightTimeoutError("Page couldn't charge all the images")
        except PlaywrightTimeoutError:
            raise
        finally:
            await self.__close_page(page)
      

        chapters_dict = {}

        for i, tag in enumerate(tags, start=1):
            if tag.has_attr("alt") and "InManga" in tag["alt"]:
                chapters_dict[f"Pagina {i}"] = tag.get("src", "N/A")
        
        return chapters_dict
    