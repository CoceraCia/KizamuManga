from utils import WebScrapping

def main():
    ws = WebScrapping()
    manga_name = input("Search for a manga->")
    mangas_result_set = ws.search_manga(manga_name)
    selected_manga = int(input("Select one of the mangas->"))
    manga_url = ws.select_manga(mangas_result_set, selected_manga)
    manga_list = ws.show_chapters(manga_url)
    print(manga_url)
if __name__ == "__main__":
    main()