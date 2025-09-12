from bs4 import BeautifulSoup

from playwright.async_api import Error, TimeoutError as PlaywrightTimeoutError, Page

from tenacity import retry, stop_after_attempt, wait_exponential

from utils.logger import Logger
from utils.general_tools import extract_num
from .interface import ScraperInterface
from .base import ScraperBase, MangaError

import time

BASE_URL = "https://zonatmo.com/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36"
}


class ZonaTMO(ScraperBase, ScraperInterface):
    """Scraper for ZonaTMO site to fetch manga info and images."""

    def __init__(self):
        """Initialize ZonaTMO scraper with logging."""
        super().__init__()
        self.logger = Logger("scraping.zonatmo")

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
        title = title.replace(" ", "+")
        url = f"{BASE_URL}library?order_item=likes_count&order_dir=desc&title={title}&_pg=1&filter_by=title&type=&demography=&status=&translation_status=&webcomic=&yonkoma=&amateur=&erotic="
        try:
            page = await self.context.new_page()
            await page.set_extra_http_headers(HEADERS)
            await page.goto(url, wait_until="domcontentloaded", timeout=3000)
            try:
                await page.wait_for_selector("div.element:nth-child(1) > a:nth-child(1)", timeout=3000)
            except Error as e:
                print("Manga not found")
                return
            html = await page.content()
        except Error as e:
            raise MangaError("Manga not found") from e
        finally:
            await self.__close_page(page)

        soup = BeautifulSoup(html, "html.parser")
        manga_urls = soup.select(".element a")
        names = soup.select(".element h4")
        nl = {}
        for i in range(len(manga_urls)):
            name = names[i].get("title", "N/A").strip("")
            url = manga_urls[i].get("href")
            
            nl[name] = url
        if nl is not None:
            return nl
        else:
            print("Manga not found")
            raise MangaError

    @retry(**_RETRY_KW)
    async def get_chapters_by_mangaurl(self, manga_url) -> dict:
        """Return chapters for a manga as {chapter_name: URL}, sorted by chapter number."""
        page = None
        try:
            page = await self.context.new_page()
            await page.set_extra_http_headers(HEADERS)
            await page.goto(manga_url, wait_until="domcontentloaded")
            time.sleep(1)
            if await page.locator("#accept-btn").count() > 0:
                if await page.locator("#accept-btn").is_visible():
                    await page.locator("#accept-btn").click(no_wait_after=True)
            try:
                print("trying")
                await page.wait_for_selector("#show-chapters", timeout=1000)
                await page.click("#show-chapters", no_wait_after=True, timeout=1000)
            except TimeoutError as e:
                print("didnt find it")
            print("success")
            locators = await page.locator(".upload-link").all()
            i = 0
            for loc in locators:
                i += 1
                print(i)
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            chaps = soup.select(".upload-link")

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
    