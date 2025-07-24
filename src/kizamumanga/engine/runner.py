"""src/kizamumanga/engine/runner.py
KizamuManga - Engine runner module for managing manga downloads."""
import asyncio
import os
import re
import shutil
import socket

from handlers import ArgsHandler
from scraping import WeebCentral, ScraperInterface, MangaError
from utils import LoadingSpinner, export_to_cbz, Ascii
from utils.logger import Logger
from .downloader import MangaDownloader
from .config import Config, BASE_PNGS_PATH, AVAILABLE_WBSITES, PROJECT_ROOT


class Runner:
    """Runner class to handle the manga downloading process.
    This class initializes the necessary components, retrieves manga and chapter information,
    and manages the downloading of chapters."""

    def __init__(self):
        self.logger = Logger("engine.runner")
        # Check if there's args
        self.args = ArgsHandler().setup_args()
        if self.args.command is None:
            print("Invalid syntaxis: must be 'search', 'install' or 'config'")
            self.logger.error("No arguments provided")
            raise SyntaxError
        self.logger.info(f"Arguments received: {self.args}")
        self.logger.info(f"Temporary PNGs path created: {BASE_PNGS_PATH}")

        # retrieve config.yaml atr
        self.config: Config = Config()
        self.logger.info(f"Config loaded: {self.config.get_config_params()}")

        # retrieve the selected scrapper
        self.ws: ScraperInterface = None

        # Initialize
        self.mdownloader: MangaDownloader = None
        self.sem: asyncio.Semaphore = None
        self.ls: LoadingSpinner = None

        if self.args.command != "config":
            self.__set_up()

    def __set_up(self):
        # retrieve the selected scrapper
        self.ws: ScraperInterface = None
        match self.config.manga_website:
            case "weeb_central":
                self.ws = WeebCentral()
            case _:
                print(f"Please choose a valid website: {AVAILABLE_WBSITES}")
                raise ValueError(f"The website you selected is not available: {self.config.manga_website}")
        self.logger.info(f"Scraper initialized and selected: {self.ws.__class__.__name__}")

        # Initialize
        self.mdownloader = MangaDownloader(self.ws)
        self.logger.info("MangaDownloader initialized")
        self.sem = asyncio.Semaphore(self.config.multiple_tasks)
        self.logger.info(f"Semaphore initialized with {self.config.multiple_tasks} tasks")
        self.ls = LoadingSpinner()
        self.logger.info("LoadingSpinner initialized")

    async def run(self):
        """Main method to run the manga downloading process."""
        try:
            if self.args.command == "config":
                await self.modify_config()
                return

            await self.ws.set_up()
            self.logger.info("Scraper set up completed")

            if self.args.command == "search" or self.args.command == "install":
                chapters = await self.search()
                self.logger.info("Chapters retrieved")
                if self.args.command == "install":
                    await self.install(chapters)
                    self.logger.info("Manga chapters installed")
        except socket.gaierror as e:
            self.logger.exception(f"Network error: {e}")
            raise KeyboardInterrupt from e
        except socket.error as e:
            self.logger.exception(f"Socket error: {e}")
            raise KeyboardInterrupt from e
        except MangaError as e:
            self.logger.exception(f"Manga error: {e}")  
        except asyncio.exceptions.CancelledError as e:
            self.logger.exception(f"CancelledError during run(): {e}")
            raise KeyboardInterrupt from e
        except ValueError as e:
            self.logger.exception(f"ValueError during run(): {e}")
            raise KeyboardInterrupt from e
        except FileNotFoundError as e:
            self.logger.exception(f"FileNotFoundError during run(): {e}")
            raise KeyboardInterrupt from e
        except (Exception, BaseException) as e:
            self.logger.exception(f"Unexpected error during run(): {e}")
            raise KeyboardInterrupt from e
        finally:
            await self.close()

    async def modify_config(self) -> bool:
        """Method to modify the configuration settings."""
        if self.args.website is not None:
            self.config.set_manga_website(self.args.website)
            self.logger.info(f"Website changed to {self.args.website}")
        if self.args.cbz_path is not None:
            self.config.set_cbz_path(self.args.cbz_path)
            self.logger.info(f"CBZ path changed to {self.args.cbz_path}")
        if self.args.multiple_tasks is not None:
            self.config.set_mult_downloads(self.args.multiple_tasks)
            self.logger.info(
                f"Multiple tasks changed to {self.args.multiple_tasks}")

    async def search(self) -> dict:
        """Method to search for mangas and retrieve chapters."""
        manga_name = self.args.name
        self.ls.start("Retrieving mangas")
        mangas_retrieved = await self.ws.get_mangas_by_title(manga_name)
        self.logger.info(f"Mangas retrieved: {len(mangas_retrieved)}")
        self.ls.end()

        print("AVAILABLE MANGAS:")
        for i, key in enumerate(mangas_retrieved.keys(), start=0):
            print(f"{i} - {key}")

        try:
            # User selects the manga
            n = int(input("Select one of the mangas, just the number->"))
            if n < 0 or n > len(mangas_retrieved):
                raise ValueError("user selected a non existent manga")
        except ValueError as e:
            self.logger.exception(f"Invalid input for manga selection: {e}")
            return

        for i, (key, value) in enumerate(mangas_retrieved.items(), start=0):
            if i == n:
                manga_name = key
                href = value
                self.logger.info(f"Selected manga: {manga_name} with href: {href}")
                break

        # Retrieve all the chapters
        self.ls.start("Retrieving chapters")
        chapters = await self.ws.get_chapters_by_mangaurl(href)
        self.ls.end()
        self.logger.info(f"Chapters retrieved: {len(chapters)}")
        
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
                self.logger.info("User chose to view all chapters")
                for chap in chapters.keys():
                    print(chap)
        return chapters

    async def install(self, chapters: dict):
        """Method to install the selected manga chapters."""
        manga_name = self.args.name
        download_all = True if self.args.chap is None else False
        manga_path = f"{self.config.cbz_path}/{manga_name}"
        os.makedirs(manga_path, exist_ok=True)
        tasks = []

        if download_all is True:
            self.logger.info("Downloading all chapters")
            for chap, href in chapters.items():
                pngs_path = f"{BASE_PNGS_PATH}/{manga_name}/{chap}"
                tasks.append(
                    self.__download_chap(
                        pngs_path=pngs_path,
                        manga_path=manga_path,
                        manga_name=manga_name,
                        chap=chap,
                        chap_url=href,
                    )
                )
        else:
            pattern = r"^(\d+)-(\d+)$"
            if not re.match(pattern, self.args.chap):
                print(
                    "Invalid chapters format.\nREMEMBER-> a single number (e.g., 5), a range (e.g., 9-18), or 'all' for all chapters"
                )
                self.logger.debug(
                    f"Invalid chapter range format trying to download {self.args.name}, with chapters {self.args.chap}")
                raise ValueError
            chap_to_download = self.args.chap.split("-")

            self.logger.info(f"Downloading chapters in range: {chap_to_download}")
            for i, (chap, href) in enumerate(chapters.items(), start=1):
                if i >= int(chap_to_download[0]) and i <= int(chap_to_download[1]):
                    pngs_path = f"{BASE_PNGS_PATH}/{manga_name}/{chap}"
                    tasks.append(
                        self.__download_chap(
                            pngs_path=pngs_path,
                            manga_path=manga_path,
                            manga_name=manga_name,
                            chap=chap,
                            chap_url=href,
                        )
                    )
        await asyncio.gather(*tasks)
        self.logger.info(f"All tasks completed for {manga_name}")
        Ascii().thank_you_for_downloading()

    async def close(self):
        """Method to close the runner and clean up resources."""
        try:
            if self.ls is not None:
                if self.ls.state is not None:
                    self.ls.end()
                    self.logger.info("LoadingSpinner ended")
                if os.path.exists(BASE_PNGS_PATH):
                    shutil.rmtree(BASE_PNGS_PATH)
                    self.logger.info(f"Temporary PNGs path {BASE_PNGS_PATH} removed")
                await asyncio.shield(self.ws.close())
                self.logger.info("Scraper closed")

                tasks = [
                    t for t in asyncio.all_tasks() if t is not asyncio.current_task()
                ]

                for task in tasks:
                    self.logger.info(f"Cancelling task: {task.get_name()}")
                    task.cancel()
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        self.logger.error(f"Task {i} finished with exception: {result}")
        except asyncio.exceptions.CancelledError as e:
            self.logger.exception(f"CancelledError during close(): {e}")
        except Exception as e:
            raise KeyboardInterrupt from e

    async def __download_chap(self, pngs_path, manga_path, manga_name, chap, chap_url):
        filename = f"{manga_name}-{chap}"
        if not os.path.exists(f"{manga_path}/{filename}.cbz"):
            async with self.sem:
                self.ls.start("Downloading")
                os.makedirs(pngs_path, exist_ok=True)
                if await asyncio.shield(
                    self.mdownloader.download_chap(
                        path=pngs_path, chapter_url=chap_url)
                ):
                    self.logger.info(f"Chapter {chap} downloaded successfully")
                else:
                    self.logger.error(f"Failed to download chapter {chap}")
                self.ls.end()
                export_to_cbz(pngs_path, manga_path, filename)
                self.logger.info(f"Exported chapter {chap} to CBZ format")
                shutil.rmtree(pngs_path)
                self.logger.info(f"Temporary PNGs path {pngs_path} removed")
        else:
            self.logger.info(f"Chapter {chap} already exists in CBZ format")
