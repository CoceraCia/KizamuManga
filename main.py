from utils import WebScrapping


def main():
    ws = WebScrapping(verify=False)
    try:
        # Retrieve mangas by title
        title = input("Input manga title->")
        mangas_retrieved = ws.get_mangas_by_title(title)
        print("AVAILABLE MANGAS:")
        for i, key in enumerate(mangas_retrieved.keys(), start=0):
            print(f"{i} - {key}")
            
        # User selects the manga
        n = int(input("Select one of the mangas, just the number->"))
        for i, value in enumerate(mangas_retrieved.values(), start=0):
            if i == n:
                href = value
                break
        print(href)
        
        # Retrieve all the chapters
        chapters = ws.get_chapters_by_mangaurl(href)
        
        print("AVAILABLE CHAPTERS")
        for key in chapters.keys():
            print(f"- {key}")

        download_all = True if str(input("Download all chapters? y/n"))  == "y" else False
        
        if download_all is True:
            None
            
        ws.close()
    except Exception as e:
        print(e)
        ws.close()


if __name__ == "__main__":
    main()
