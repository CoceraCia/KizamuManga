import json
import os
import threading
import tempfile
import shutil

from utils.scraping import WeebCentral
from utils.general_tools import export_to_cbz
from utils.loading_spinner import LoadingSpinner


with open("config.json", "r") as f:
    config:dict = json.load(f)
PNGS_PATH = tempfile.mkdtemp()
print(PNGS_PATH)
CBZ_PATH = config.get("cbz_path")


def main():
    print(CBZ_PATH)
    ws = WeebCentral(verify=False)
    ls = LoadingSpinner()

    try:
        # Retrieve mangas by title
        title = input("Input manga title->")
        try:
            ls.start("Retrieving mangas")
            mangas_retrieved = ws.get_mangas_by_title(title)
            ls.end()
        except ValueError as e:
            ls.end()
            print(e)
            raise KeyboardInterrupt


        print("AVAILABLE MANGAS:")
        for i, key in enumerate(mangas_retrieved.keys(), start=0):
            print(f"{i} - {key}")

        # User selects the manga
        n = int(input("Select one of the mangas, just the number->"))
        for i, (key, value) in enumerate(mangas_retrieved.items(), start=0):
            if i == n:
                manga_name = key
                href = value
                break

        # Retrieve all the chapters
        chapters = ws.get_chapters_by_mangaurl(href)

        print("AVAILABLE CHAPTERS")
        for key, value in chapters.items():
            print(f"- {key}:{value}")

        download_all = True if str(
            input("Download all chapters? y/n->")) == "y" else False

        manga_path = f"{CBZ_PATH}/{manga_name}"
        os.makedirs(manga_path, exist_ok=True)


        if download_all is True:
            for chap, href in chapters.items():
                ls.start(f"Downloading chapter {chap}")
                pngs_path = f"{PNGS_PATH}/{manga_name}/{chap}"
                os.makedirs(pngs_path, exist_ok=True)
                ws.download_chapter_by_url(href, pngs_path)
                ls.end()
                export_to_cbz(pngs_path, manga_path, f"{manga_name}-{chap}")
                shutil.rmtree(pngs_path)

        ws.close()

    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        print(e)
    finally:
        print("Bye")
        shutil.rmtree(PNGS_PATH)
        ls.end()
        ws.close()

if __name__ == "__main__":
    main()
