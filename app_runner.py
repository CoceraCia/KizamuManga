import asyncio
import os
import re
import shutil
from config import CBZ_PATH, MANGA_WEBSITE, PNGS_PATH
from handlers import ArgsHandler
from utils.scraping import WeebCentral, ScraperInterface
from utils import LoadingSpinner, export_to_cbz
from utils import MangaDownloader


class AppRunner():
    def __init__(self):
        self.args = ArgsHandler().setup_args()
        if self.args.command is None:
            print("Invalid syntaxis")
            raise ValueError
        print(self.args)
        self.ws: ScraperInterface = None
        match MANGA_WEBSITE:
            case "weebcentral":
                self.ws = WeebCentral()

        # Asyncio semaphor
        self.mdownloader = MangaDownloader(self.ws)
        self.sem = asyncio.Semaphore(5)
        self.ls = LoadingSpinner()

    async def run(self):
        try:
            await self.ws.set_up()
            if self.args.command == "search" or self.args.command == "install":
                manga_name = self.args.name
                self.ls.start("Retrieving mangas")
                mangas_retrieved = await self.ws.get_mangas_by_title(manga_name)
                self.ls.end()

                print("AVAILABLE MANGAS:")
                for i, key in enumerate(mangas_retrieved.keys(), start=0):
                    print(f"{i} - {key}")

                try:
                    # User selects the manga
                    n = int(input("Select one of the mangas, just the number->"))
                except ValueError:
                    print("Invalid syntax-use a number")

                for i, (key, value) in enumerate(mangas_retrieved.items(), start=0):
                    if i == n:
                        manga_name = key
                        href = value
                        break
                # Retrieve all the chapters
                self.ls.start("Retrieving chapters")
                chapters = await self.ws.get_chapters_by_mangaurl(href)
                self.ls.end()
                if self.args.command == "search":
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
                elif self.args.command == "install":
                    download_all = True if self.args.chap == "all" else False
                    manga_path = f"{CBZ_PATH}/{manga_name}"
                    os.makedirs(manga_path, exist_ok=True)
                    tasks = []

                    if download_all is True:
                        for chap, href in chapters.items():
                            pngs_path = f"{PNGS_PATH}/{manga_name}/{chap}"
                            tasks.append(
                                    self.__download_chap(
                                        pngs_path=pngs_path,
                                        manga_path=manga_path,
                                        manga_name=manga_name,
                                        chap=chap,
                                        chap_url=href
                                    )
                                )
                        await asyncio.gather(*tasks)

                    else:
                        pattern = r"^(\d+)-(\d+)$"
                        if not re.match(pattern, self.args.chap) or self.args.chap != "all":
                            print(
                                "Invalid chapters format.\nREMEMBER-> a single number (e.g., 5), a range (e.g., 9-18), or 'all' for all chapters")
                            raise ValueError
                        chap_to_download = self.args.chap.split("-")

                        for i, (chap, href) in enumerate(chapters.items(), start=1):
                            if i >= int(chap_to_download[0]) and i <= int(chap_to_download[1]):
                                pngs_path = f"{PNGS_PATH}/{manga_name}/{chap}"
                                tasks.append(
                                    self.__download_chap(
                                        pngs_path=pngs_path,
                                        manga_path=manga_path,
                                        manga_name=manga_name,
                                        chap=chap,
                                        chap_url=href
                                    )
                                )
                        await asyncio.gather(*tasks)
        except (ValueError, Exception, BaseException) as e:
            print(e)
            raise
        finally:
            try:
                if self.ls.state is not None:
                    self.ls.end()
                if os.path.exists(PNGS_PATH):
                    shutil.rmtree(PNGS_PATH)
                await asyncio.shield(self.ws.close())
            
                tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

                for task in tasks:
                    task.cancel()
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        print(f"Tarea {i} terminó con excepción: {result}")
                print("\nGoodBye!")
            except asyncio.exceptions.CancelledError:
                raise
            except Exception as e:
                print(f"Error durante close(): {e}")
            

    async def __download_chap(self, pngs_path, manga_path, manga_name, chap, chap_url):
        async with self.sem:
            self.ls.start("Downloading")
            os.makedirs(pngs_path, exist_ok=True)
            await asyncio.shield(self.mdownloader.download_chap(path=pngs_path, chapter_url=chap_url))
            self.ls.end()
            export_to_cbz(pngs_path, manga_path, f"{manga_name}-{chap}")
            shutil.rmtree(pngs_path)
            print(f"Downloaded {chap}")
