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
    def __init__(self, verify=True):
        self.verify = verify
        p = sync_playwright().start()
        self.browser = p.chromium.launch(headless=True)
        self.page = self.browser.new_page()

    def close(self):
        self.page.close()
        self.browser.close()

    def get_mangas_by_title(self, title: str):
        title = title.replace(" ", "+")
        url = f"{BASE_URL}/search?text={title}&sort=Best+Match&order=Descending&official=Any&anime=Any&adult=Any&display_mode=Full+Display"
        self.page.goto(url)
        try:
            self.page.wait_for_selector("#search-results > article:nth-child(1)", timeout=1500)
        except Error:
            print("Manga not found")
            return None         
        html = self.page.content()

        soup = BeautifulSoup(html, "html.parser")
        manga_names = soup.select("a.line-clamp-1")

        nl = {}

        for item in manga_names:
            nl[item.text.strip()] = item.get("href", "N/A")

        return nl

    def get_chapters_by_mangaurl(self, manga_url):
        self.page.goto(manga_url)
        self.page.wait_for_selector("#chapter-list > button")
        self.page.click("#chapter-list > button")
        self.page.wait_for_timeout(1200)
        html = self.page.content()

        soup = BeautifulSoup(html, "html.parser")
        tags = soup.find_all(
            "a", class_="hover:bg-base-300 flex-1 flex items-center p-2"
        )

        nl = {}
        for tag in tags:
            href = tag.get("href", "N/A")
            for span in tag.find_all("span"):
                if span.has_attr("class") and span["class"] == []:
                    nl[span.text.strip()] = href.strip()
                    break
            
        sorted_nl = {}
        for chap, href in nl.items():
            
        
        return sorted(nl, key=extract_num)

    def download_chapter_by_url(self, manga_url, path):
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
                response = requests.get(src, headers=HEADERS, verify=self.verify)
                # Downloading png
                if response.status_code == 200:
                    with open(f'{path}/{tag.get("alt")}.png', "wb") as f:
                        f.write(response.content)
                else:
                    print(f"Couldn't download the image: {src}")
        return True
