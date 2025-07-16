import warnings

warnings.filterwarnings("ignore", category=ResourceWarning)

import json
import os
import threading
import tempfile
import shutil
import asyncio
import aioconsole
import sys

from utils.scraping import WeebCentral
from utils.general_tools import export_to_cbz
from utils.loading_spinner import LoadingSpinner

with open("config.json", "r") as f:
    config: dict = json.load(f)
PNGS_PATH = tempfile.mkdtemp()
print(PNGS_PATH)
CBZ_PATH = config.get("cbz_path")
sem = asyncio.Semaphore(5)

async def main():
    interrupted = False
    print(CBZ_PATH)
    ws = WeebCentral(verify=False)
    await ws.init_playwright()
    ls = LoadingSpinner()
    print(sys.platform)

    async def close(interrupted=False):
        try:
            if ls.state is not None:
                ls.end()
            if os.path.exists(PNGS_PATH):
                shutil.rmtree(PNGS_PATH)
            print("\nGoodBye!")
            if not interrupted:
                await asyncio.shield(ws.close())
            await close_tasks()
        except asyncio.exceptions.CancelledError:
            raise
        except Exception as e:
            print(f"Error durante close(): {e}")

    try:
        title = await aioconsole.ainput("Input manga title->")
        ls.start("Retrieving mangas")
        mangas_retrieved = await ws.get_mangas_by_title(title)
        ls.end()

        print("AVAILABLE MANGAS:")
        for i, key in enumerate(mangas_retrieved.keys(), start=0):
            print(f"{i} - {key}")

        try:
            # User selects the manga
            n = int(input("Select one of the mangas, just the number->"))
            for i, (key, value) in enumerate(mangas_retrieved.items(), start=0):
                if i == n:
                    manga_name = key
                    href = value
                    break
        except ValueError:
            print("Invalid syntax")

        # Retrieve all the chapters
        chapters = await ws.get_chapters_by_mangaurl(href)

        print("AVAILABLE CHAPTERS")
        for key, value in chapters.items():
            print(f"- {key}:{value}")

        download_all = (
            True if str(input("Download all chapters? y/n->")) == "y" else False
        )

        manga_path = f"{CBZ_PATH}/{manga_name}"
        os.makedirs(manga_path, exist_ok=True)

        if download_all is True:
            tasks = []
                
            for chap, href in chapters.items():
                pngs_path = f"{PNGS_PATH}/{manga_name}/{chap}"
                tasks.append(
                    download_chapter(ws=ws,
                                 chap=chap,
                                 href=href,
                                 manga_name=manga_name,
                                 manga_path=manga_path,
                                 pngs_path=pngs_path,
                                 ls=ls)
                             )
            await asyncio.gather(*tasks)
            
        await asyncio.shield(ws.close())
        
    except (ValueError, Exception, BaseException):
        await asyncio.shield(close(interrupted=True))
        raise


async def download_chapter(ws, chap, href, manga_name, manga_path ,pngs_path, ls):
    async with sem:
        ls.start(f"Downloading chapter")
        pngs_path = f"{PNGS_PATH}/{manga_name}/{chap}"
        os.makedirs(pngs_path, exist_ok=True)
        await asyncio.shield(ws.download_chapter_by_url(href, pngs_path))
        ls.end()
        export_to_cbz(pngs_path, manga_path, f"{manga_name}-{chap}")
        shutil.rmtree(pngs_path)
        print(f"Downloaded {chap}")

async def close_tasks():
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    
    for task in tasks:
        task.cancel()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Tarea {i} terminó con excepción: {result}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (asyncio.exceptions.CancelledError, KeyboardInterrupt):
        pass
    finally:
        sys.stderr = open(os.devnull, "w")
