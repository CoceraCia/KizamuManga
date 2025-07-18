import json
import os, argparse
import re
import tempfile
import shutil
import asyncio
import sys

from utils.config_handler import ConfigHandler
from utils.scraping import WeebCentral
from utils.general_tools import export_to_cbz
from utils.loading_spinner import LoadingSpinner

# Files managment
with open("config.json", "r") as f:
    config: dict = json.load(f)
PNGS_PATH = tempfile.mkdtemp()
print(PNGS_PATH)
CBZ_PATH = config.get("cbz_path")
manga_website = config.get("manga_website")

# Asyncio semaphor
sem = asyncio.Semaphore(5)


async def main():
    args = await setup_args()
    print(args)

    print(CBZ_PATH)
    cf = ConfigHandler()
    if not cf.manga_web_is_available(manga_website):
        print(cf.retrieve_available_websites(str=True))
    ws = WeebCentral(verify=False)
    await ws.init_playwright()
    ls = LoadingSpinner()

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
        if args.command == "search" or args.command == "install":
            manga_name = args.name
            ls.start("Retrieving mangas")
            mangas_retrieved = await ws.get_mangas_by_title(manga_name)
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
            ls.start("Retrieving chapters")
            chapters = await ws.get_chapters_by_mangaurl(href)
            ls.end()
            if args.command == "search":
                print(f"AVAILABLE CHAPTERS: {len(chapters.keys())}")
                view_all_chapters = (
                True
                if str(
                    input(
                        "Do you want to view all chapters? (Note: some may include refill chapters) [y/n] -> "
                    )
                )
                == "y"
                else False
                )
                if view_all_chapters:
                    for chap in chapters.keys():
                        print(chap)
                    
            elif args.command == "install":
                download_all = True if args.chap == "all" else False
                manga_path = f"{CBZ_PATH}/{manga_name}"
                os.makedirs(manga_path, exist_ok=True)
                tasks = []
                
                if download_all is True:
                    for chap, href in chapters.items():
                        pngs_path = f"{PNGS_PATH}/{manga_name}/{chap}"
                        tasks.append(
                            download_chapter(
                                ws=ws,
                                chap=chap,
                                href=href,
                                manga_name=manga_name,
                                manga_path=manga_path,
                                pngs_path=pngs_path,
                                ls=ls,
                            )
                        )
                    await asyncio.gather(*tasks)

                else:
                    pattern = r"^(\d+)-(\d+)$"
                    if not re.match(pattern, args.chap) or args.chap != "all":
                        print("Invalid chapters format.\nREMEMBER-> a single number (e.g., 5), a range (e.g., 9-18), or 'all' for all chapters")
                        raise ValueError
                    chap_to_download = args.chap.split("-")
                    
                    for i, (chap, href) in enumerate(chapters.items(), start=1):
                        if i >= int(chap_to_download[0]) and i <= int(chap_to_download[1]):
                            pngs_path = f"{PNGS_PATH}/{manga_name}/{chap}"
                            tasks.append(
                                download_chapter(
                                    ws=ws,
                                    chap=chap,
                                    href=href,
                                    manga_name=manga_name,
                                    manga_path=manga_path,
                                    pngs_path=pngs_path,
                                    ls=ls,
                                )
                            )
                    await asyncio.gather(*tasks)
    except (ValueError, Exception, BaseException) as e:
        print(e)
        raise
    finally:
        await asyncio.shield(close())


async def setup_args():
    # Initialize main parser
    parser = argparse.ArgumentParser(description="Manga scrapper")

    # Initialize subparsers
    subparsers = parser.add_subparsers(dest="command")

    # config subparser
    sub_config = subparsers.add_parser("config", help="update configuration")
    # config args
    sub_config.add_argument("--website", help="website where the scrapping happens")
    sub_config.add_argument("--cbz_path", help="path where the mangas are located")

    # install subparser
    sub_install = subparsers.add_parser("install", help="install a manga by it's name")
    
    # install args
    sub_install.add_argument("--name",
                              help="Install the manga by its name (e.g., One Piece)",
                              required=True)
    sub_install.add_argument("--chap",
                             help="Chapters to download: a single number (e.g., 5), a range (e.g., 9-18), or 'all' for all chapters",
                             required=True)

    # search subparser
    sub_search = subparsers.add_parser("search", help="name of the manga to search")
    # search args
    sub_search.add_argument("--name", help="The name of a manga", required=True)

    return parser.parse_args()


async def download_chapter(ws, chap, href, manga_name, manga_path, pngs_path, ls):
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
