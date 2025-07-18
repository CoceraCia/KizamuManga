import asyncio, aiohttp

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Error, TimeoutError as PlaywrightTimeoutError
from utils.general_tools import extract_num

BASE_URL = "https://weebcentral.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36"
}


class WeebCentral:
    """
    Class to interact with the WeebCentral website to search for manga,
    retrieve chapters, and download them.
    Uses Playwright for browser automation and BeautifulSoup for HTML parsing.
    """

    def __init__(self, verify=True):
        """
        Initialize the WeebCentral instance with a headless browser.

        Args:
            verify (bool): Whether to verify SSL certificates when downloading images.
                           Default is True.
        """
        self.verify = verify
        self.browser = None
        self.context = None

    async def init_playwright(self):
        p = await async_playwright().start()
        self.browser = await p.chromium.launch(headless=True)
        self.context = await self.browser.new_context()

    async def close(self):
        """
        Close the Playwright page and browser.
        """
        # Close page
        try:
            await asyncio.wait_for(self.context.close(), timeout=1)
            print("Page closed successfully")
        except Exception as e:
            print(f"⚠️ Error closing page: {type(e).__name__}: {e}")

        # Close browser
        try:
            await asyncio.wait_for(self.browser.close(), timeout=1)
            print("Browser closed successfully")
        except Exception as e:
            print(f"⚠️ Error closing browser: {e}")

    async def get_mangas_by_title(self, title: str):
        """
        Search for manga by title on WeebCentral.

        Args:
            title (str): The title of the manga to search.

        Returns:
            dict or None: A dictionary with manga names as keys and partial URLs as values.
                          Returns None if no results are found.
        """
        title = title.replace(" ", "+")
        url = f"{BASE_URL}/search?text={title}&sort=Best+Match&order=Descending&official=Any&anime=Any&adult=Any&display_mode=Full+Display"
        async with await self.context.new_page() as page:
            try:
                await page.goto(url)
                await page.wait_for_selector(
                    "#search-results > article:nth-child(1)", timeout=1500
                )
                html = await page.content()
            except Error:
                raise ValueError("Manga not found")

        soup = BeautifulSoup(html, "html.parser")
        manga_names = soup.select("a.line-clamp-1")

        nl = {}
        for item in manga_names:
            nl[item.text.strip()] = item.get("href", "N/A")

        return nl

    async def get_chapters_by_mangaurl(self, manga_url):
        """
        Retrieve available chapters for a given manga URL.

        Args:
            manga_url (str): The full URL of the manga.

        Returns:
            dict: A sorted dictionary with chapter names as keys and chapter URLs as values.
        """
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

    async def download_chapter_by_url(self, manga_url, path):
        """
        Download all pages of a manga chapter to the specified local folder.

        Args:
            manga_url (str): The URL of the chapter to download.
            path (str): The local folder path to save the images.

        Returns:
            bool: True if the download was successful.
        """
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

        async with aiohttp.ClientSession() as session:
            for tag in tags:
                if tag.has_attr("alt") and "Page" in tag["alt"]:
                    url = tag.get("src", "N/A")
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
                                    f'{path}/{tag.get("alt")}.png', "wb"
                                ) as f:
                                    f.write(content)
                                break
                        except asyncio.TimeoutError:
                            print("TimeoutError")
                            pass
                    