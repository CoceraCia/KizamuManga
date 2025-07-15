import requests
import os


from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Error
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
        p = sync_playwright().start()
        self.browser = p.chromium.launch(headless=True)
        self.page = self.browser.new_page()

    def close(self):
        """
        Close the Playwright page and browser.
        """
        # Close page
        try:
            self.page.close()
            print("Page closed successfully")
        except Exception as e:
            print(f"⚠️ Error closing page: {e}")
        
        # Close browser
        try:
            self.browser.close()
            print("Browser closed successfully")
        except Exception as e:
            print(f"⚠️ Error closing browser: {e}")

    def get_mangas_by_title(self, title: str):
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
        self.page.goto(url)
        try:
            self.page.wait_for_selector("#search-results > article:nth-child(1)", timeout=1500)
        except Error:
            raise ValueError("Manga not found")
        html = self.page.content()

        soup = BeautifulSoup(html, "html.parser")
        manga_names = soup.select("a.line-clamp-1")

        nl = {}
        for item in manga_names:
            nl[item.text.strip()] = item.get("href", "N/A")

        return nl

    def get_chapters_by_mangaurl(self, manga_url):
        """
        Retrieve available chapters for a given manga URL.

        Args:
            manga_url (str): The full URL of the manga.

        Returns:
            dict: A sorted dictionary with chapter names as keys and chapter URLs as values.
        """
        self.page.goto(manga_url)
        self.page.wait_for_selector("#chapter-list > button")
        self.page.click("#chapter-list > button")
        self.page.wait_for_timeout(1200)
        html = self.page.content()

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

    def download_chapter_by_url(self, manga_url, path):
        """
        Download all pages of a manga chapter to the specified local folder.

        Args:
            manga_url (str): The URL of the chapter to download.
            path (str): The local folder path to save the images.

        Returns:
            bool: True if the download was successful.
        """
        try:
            self.page.goto(manga_url)

            self.page.wait_for_timeout(2000)
            self.page.wait_for_selector("img[alt *= 'Page']", timeout=10000)
            html = self.page.content()

            soup = BeautifulSoup(html, "html.parser")
            tags = soup.find_all("img")
        
            for tag in tags:
                if tag.has_attr("alt") and "Page" in tag["alt"]:
                    src = tag.get("src", "N/A")
                    if src == "N/A":
                        print("No image found")
                        return
                    while True:
                        try:
                            response = requests.get(src, headers=HEADERS, verify=self.verify, timeout=15)
                            break
                        except requests.exceptions.Timeout:
                            print("Error downloading the chapter. Trying again")
                    if response.status_code == 200:
                        with open(f'{path}/{tag.get("alt")}.png', "wb") as f:
                            f.write(response.content)
                    else:
                        raise ValueError(f"Couldn't download the image: {src}")
        except Exception:
            raise KeyboardInterrupt()
        
        return True
