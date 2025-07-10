import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE_URL = "https://weebcentral.com"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36'}
class WebScrapping:
    def __init__(self, verify=True):
        self.verify = verify


    def setup_search_page(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_selector("#search-results > article:nth-child(1)")
            html = page.content()
            page.close()
            return html
        
    def setup_manga_page(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_selector("#chapter-list > button")
            page.click("#chapter-list > button")
            page.wait_for_selector("#chapter-list > div:nth-child(1) > a")
            html = page.content()
            page.close()
            return html
        
            
    
    def search_manga(self, title: str):
        title = title.replace(" ", "+")
        url = f"{BASE_URL}/search?text={title}&sort=Best+Match&order=Descending&official=Any&anime=Any&adult=Any&display_mode=Full+Display"
        html = self.setup_search_page(url)
        
        soup = BeautifulSoup(html, "html.parser")
        manga_names = soup.select("a.line-clamp-1")
        
        print("📖 - AVAILABLE MANGAS:")
        for i, item in enumerate(manga_names, start=1):
            print(f"{i}-{item.text}")
            print(item["href"])
    
        return manga_names
    
    def select_manga(self, manga_names, num):
          for i, item in enumerate(manga_names, start=1):
            if i == num:
                return item["href"]
              
    def show_chapters(self, manga_url):
        html = self.setup_manga_page(manga_url)
        
        soup = BeautifulSoup(html, "html.parser")
        tags = soup.find_all("a", class_="hover:bg-base-300 flex-1 flex items-center p-2")
        
            
            
        
        
        

    def export_to_file(self, html):
        with open("resultados.html", "w", encoding="utf-8") as f:
            f.write(html.prettify())  # O usa str(txt)
