from utils.scraping import WeebCentral
import os

from utils.general_tools import export_to_cbz

PNGS_PATH = "files/pngs"
CBZ_PATH = "files/mangas"

def main():
    ws = WeebCentral(verify=False)
    
    try:
        # Retrieve mangas by title
        title = input("Input manga title->")
        mangas_retrieved = ws.get_mangas_by_title(title)
        if mangas_retrieved is None:
            return
        
        print("AVAILABLE MANGAS:")
        for i, key in enumerate(mangas_retrieved.keys(), start=0):
            print(f"{i} - {key}")
            
        # User selects the manga
        n = int(input("Select one of the mangas, just the number->"))
        for i, (key, value)  in enumerate(mangas_retrieved.items(), start=0):
            if i == n:
                manga_name = key
                href = value
                break
        print(manga_name + "-" + href)
        
        # Retrieve all the chapters
        chapters = ws.get_chapters_by_mangaurl(href)
        
        print("AVAILABLE CHAPTERS")
        for key, value in chapters.items():
            print(f"- {key}:{value}")

        download_all = True if str(input("Download all chapters? y/n"))  == "y" else False
        
        manga_path = f"{CBZ_PATH}/{manga_name}"
        os.makedirs(manga_path, exist_ok=True)
        
        if download_all is True:
            for chap, href in chapters.items():
                pngs_path = f"{PNGS_PATH}/{manga_name}/{chap}"
                os.makedirs(pngs_path, exist_ok=True)
                ws.download_chapter_by_url(href, pngs_path)
                export_to_cbz(pngs_path, manga_path, f"{manga_name}-{chap}")
                
                
                
            
        ws.close()
    except Exception as e:
        print(e)
        ws.close()
    except KeyboardInterrupt:
        print("Goodbye senpai!!")
        ws.close()


if __name__ == "__main__":
    main()
