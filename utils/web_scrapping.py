import requests
from bs4 import BeautifulSoup

URL = "https://mangareader.to"

class WebScrapping:
    def __init__(self, verify=True):
        self.verify = verify

    def search_manga(self, title: str):
        query = title.replace(" ", "+")
        url = f"{URL}/search?keyword={query}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36'}
        
        response = requests.get(url, headers=headers, verify=self.verify)
        soup = BeautifulSoup(response.text, "html.parser")
        # self.export_to_file(soup)
        manga_names = soup.select(".manga-name a")
        
        print("📖AVAILABLE MANGAS:")
        for i, item in enumerate(manga_names, start=1):
            print(f"{i}-{item.text}")
    
        return manga_names
    
    def select_manga(self, manga_names, num):
          for i, item in enumerate(manga_names, start=1):
              if i == num:
                  return item["href"]
              
    def show_chapters(self, manga_url):
        
        

    def export_to_file(self, html):
        with open("resultados.html", "w", encoding="utf-8") as f:
            f.write(html.prettify())  # O usa str(txt)
