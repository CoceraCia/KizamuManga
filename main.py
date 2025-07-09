from utils import WebScrapping

def main():
    ws = WebScrapping(verify=False)
    manga_name = input("Search for a manga->")
    mangas_result_set = ws.search_manga(manga_name)
    selected_manga = int(input("Select one of the mangas->"))
    manga_url = ws.select_manga(mangas_result_set, selected_manga)
    print(manga)
if __name__ == "__main__":
    main()