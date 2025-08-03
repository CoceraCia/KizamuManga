"""src/kizamumanga/engine/runner.py
KizamuManga - Engine runner module for managing manga downloads."""

import asyncio
import os
import shutil
import socket
import tempfile
import time

from rich.console import Console
from handlers import ArgsHandler
from scraping import WeebCentral, ScraperInterface, MangaError
from utils import LoadingSpinner, export_to_cbz, Ascii
from utils.logger import Logger
from .downloader import MangaDownloader
from .config import Config
from .paths import CBZ_PATH, TEMP_PATH


class Runner:
    """Runner class to handle the manga downloading process.
    This class initializes the necessary components, retrieves manga and chapter information,
    and manages the downloading of chapters."""

    def __init__(self):
        self.logger = Logger("engine.runner")
        # Check if there's args
        args_handler = ArgsHandler()

        args_handler.validate_args()
        self.args = args_handler.args
        self.logger.info(f"Arguments received: {self.args}")

        # retrieve config.toml atr
        self.config: Config = Config()
        self.logger.info(f"Config loaded: {self.config.config}")

        self.console = Console()

        # retrieve the selected scrapper
        self.ws: ScraperInterface = None

        # Initialize
        self.mdownloader: MangaDownloader = None
        self.sem: asyncio.Semaphore = None
        self.ls: LoadingSpinner = None
        self.manga_name = None

        if self.args.command != "config":
            self.__set_up()

    def __set_up(self):
        self.ws: ScraperInterface = None
        match self.config.website:  # retrieve the selected scrapper
            case "weeb_central":
                self.ws = WeebCentral()
        self.logger.info(
            f"Scraper initialized and selected: {self.ws.__class__.__name__}"
        )

        self.mdownloader = MangaDownloader(self.ws)
        self.logger.info("MangaDownloader initialized")

        self.sem = asyncio.Semaphore(self.config.multiple_tasks)
        self.logger.info(
            f"Semaphore initialized with {self.config.multiple_tasks} tasks"
        )
        self.ls = LoadingSpinner()
        self.logger.info("LoadingSpinner initialized")

    async def run(self):
        """Main method to run the manga downloading process."""
        try:
            # Check if cbz_path exists
            if not os.path.exists(CBZ_PATH):
                print("Please set a valid folder for the cbz_path")
                raise FileNotFoundError(f"Folder doesn't exists at: {CBZ_PATH}")

            # Create tempPath
            os.makedirs(TEMP_PATH, exist_ok=True)
            self.logger.info(f"Temporary PNGs path created: {TEMP_PATH}")

            # -----------------execute console commands----------------
            if self.args.command == "config":
                await self.modify_config()
                return

            # set up scraper components
            await self.ws.set_up()
            self.logger.info("Scraper set up completed")

            if self.args.command == "search" or self.args.command == "install":
                chapters = await self.search()
                self.logger.info("Chapters retrieved")

                if self.args.command == "install":
                    await self.install(chapters)
                    self.logger.info("Manga chapters installed")

        except FileNotFoundError as e:
            self.logger.exception(f"FileNotFoundError during run(): {e}")
            raise KeyboardInterrupt from e
        except socket.gaierror as e:
            self.logger.exception(f"Network error: {e}")
            raise KeyboardInterrupt from e
        except socket.error as e:
            self.logger.exception(f"Socket error: {e}")
            raise KeyboardInterrupt from e
        except MangaError as e:
            self.logger.exception(f"Manga error: {e}")
            raise KeyboardInterrupt from e
        except asyncio.exceptions.CancelledError as e:
            self.logger.exception(f"CancelledError during run(): {e}")
            raise KeyboardInterrupt from e
        except RuntimeError as e:
            raise KeyboardInterrupt from e
        except ValueError as e:
            self.logger.exception(f"ValueError during run(): {e}")
            raise KeyboardInterrupt from e
        except Exception as e:
            self.logger.exception(f"Unexpected error during run(): {e}")
            raise KeyboardInterrupt from e
        finally:
            await self.close()

    async def modify_config(self) -> bool:
        """Method to modify the configuration settings."""
        if self.args.command == "config":
            if self.args.conf_comm == "dimensions":
                if self.args.device or self.args.width:
                    self.config.width = self.args.width
                    self.config.height = self.args.height
                    self.logger.info(
                        f"dimensions changed to {self.args.width}x{self.args.height}"
                    )
            elif self.args.conf_comm == "scraper":
                if self.args.website:
                    self.config.website = self.args.website
                    self.logger.info(f"Website changed to {self.args.website}")
                if self.args.multiple_tasks:
                    self.config.multiple_tasks = self.args.multiple_tasks
                    self.logger.info(
                        f"Multiple tasks changed to {self.args.multiple_tasks}"
                    )
            elif self.args.conf_comm == "output":
                if self.args.cropping_mode is not None:  # it's bool
                    self.config.cropping_mode = self.args.cropping_mode
                    self.logger.info(
                        f"Cropping_mode changed to {self.args.cropping_mode}"
                    )
                if self.args.color is not None:  # it's bool
                    self.config.color = self.args.color
                    self.logger.info(f"Color changed to {self.args.website}")
            elif self.args.conf_comm == "paths":
                if self.args.cbz_path:
                    self.config.cbz_path = self.args.cbz_path
                    self.logger.info(f"CBZ path changed to {self.args.cbz_path}")

    async def search(self) -> dict:
        """Method to search for mangas and retrieve chapters."""
        manga_name = self.args.name
        self.ls.start("Retrieving mangas")
        mangas_retrieved = await self.ws.get_mangas_by_title(manga_name)
        self.logger.info(f"Mangas retrieved: {len(mangas_retrieved)}")
        self.ls.end()

        self.console.print("[bold white]AVAILABLE MANGAS:[/bold white]")
        for i, key in enumerate(mangas_retrieved.keys(), start=0):
            self.console.print(f"[white]{i}[/white] - {key}")

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
                self.manga_name = key
                href = value
                self.logger.info(f"Selected manga: {self.manga_name} with href: {href}")
                break
        # Retrieve all the chapters
        self.ls.start("Retrieving chapters")
        chapters = await self.ws.get_chapters_by_mangaurl(href)
        self.ls.end()
        self.logger.info(f"Chapters retrieved: {len(chapters)}")

        if self.args.command == "search":
            # Display chapter count
            self.console.print(f"[bold white]AVAILABLE CHAPTERS:[/bold white] ", end="")
            print(len(chapters.keys()))

            # Ask user to view all chapters
            self.console.print(
                "Do you want to view all chapters? [i](Note: some may include extra chapters)[/i] y/n -> ",
                end="",
            )

            # Display chaps
            view_all_chapters = True if input() == "y" else False
            if view_all_chapters:
                self.logger.info("User chose to view all chapters")
                for i, chap in enumerate(chapters.keys(), start=1):
                    self.console.print(f"[bold white]{i}[/bold white] - ", end="")
                    print(chap)

        return chapters

    async def install(self, chapters: dict):
        """Method to install the selected manga chapters."""
        # self.args.chap can be int or list, thats why we need to check it first
        if self.args.chap:
            if isinstance(self.args.chap, int):
                if self.args.chap > len(chapters):
                    self.console.print(
                        f"[bold red]chapter doesn't exists. [/bold red]", end=""
                    )
                    print(f"Chapters_available -> {len(chapters)}")

                    # Logg and raise error
                    self.logger.error(f"Chapter doesn't exists -> {self.args.chap}")
                    raise ValueError("Chapter doesn't exists")
            else:
                if self.args.chap[1] > len(chapters):
                    self.console.print(f"[bold red]Invalid range. [/bold red]", end="")
                    print(f"Chapters_available -> {len(chapters)}")

                    # Logg and raise error
                    self.logger.error(
                        f"Invalid chapter range: {self.args.chap} when searching for {len(chapters)} chapters"
                    )
                    raise ValueError("Invalid chapter range")

        manga_name = self.manga_name
        download_all = True if self.args.chap is None else False
        tasks = []

        manga_path = os.path.normpath(f"{CBZ_PATH}/{manga_name}")
        os.makedirs(manga_path, exist_ok=True)

        if download_all is True:
            self.ls.start("Downloading all chapters", len(chapters))
            self.logger.info("Downloading all chapters")
            for chap, href in chapters.items():
                pngs_path = os.path.normpath(f"{TEMP_PATH}/{manga_name}/{chap}")
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
            self.ls.start("Downloading chapters", len(chapters))
            self.logger.info(f"Downloading chapters in range: {self.args.chap}")
            for i, (chap, href) in enumerate(chapters.items(), start=1):
                # If it's a range of chaps
                if isinstance(self.args.chap, list):
                    if i >= int(self.args.chap[0]) and i <= int(self.args.chap[1]):
                        pngs_path = f"{TEMP_PATH}/{manga_name}/{chap}"
                        tasks.append(
                            self.__download_chap(
                                pngs_path=pngs_path,
                                manga_path=manga_path,
                                manga_name=manga_name,
                                chap=chap,
                                chap_url=href,
                            )
                        )
                # If it's just one chap
                else:
                    if i == self.args.chap:
                        pngs_path = f"{TEMP_PATH}/{manga_name}/{chap}"
                        tasks.append(
                            self.__download_chap(
                                pngs_path=pngs_path,
                                manga_path=manga_path,
                                manga_name=manga_name,
                                chap=chap,
                                chap_url=href,
                            )
                        )
        # Wait for all tasks to be completed
        await asyncio.gather(*tasks)
        self.logger.info(f"All tasks completed for {manga_name}")

        time.sleep(1)
        Ascii().thank_you_for_downloading()
        print(f"Chapter {self.args.chap} downloaded at {manga_path}")

    async def close(self):
        """Method to close the runner and clean up resources."""
        try:
            # ---------------Closing Loading Spiner---------------
            if self.ls is not None or self.ls.progress is not None:
                if self.ls.state is not None:
                    self.ls.end()
                    self.logger.info("LoadingSpinner ended")

            # ------------------ Deleting temp_path----------------------
            if os.path.exists(TEMP_PATH):
                shutil.rmtree(TEMP_PATH)
                self.logger.info(f"Temporary PNGs path {TEMP_PATH} removed")

            # -------------------Closing WebScraping-----------------
            await asyncio.shield(self.ws.close())
            self.logger.info("Scraper closed")

            # --------------------Closing all tasks---------------------
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

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
                # self.ls.start("Downloading")
                os.makedirs(pngs_path, exist_ok=True)
                if await asyncio.shield(
                    self.mdownloader.download_chap(path=pngs_path, chapter_url=chap_url)
                ):
                    self.logger.info(f"Chapter {chap} downloaded successfully")
                else:
                    self.logger.error(f"Failed to download chapter {chap}")
                # self.ls.end()
                export_to_cbz(pngs_path, manga_path, filename)
                self.logger.info(f"Exported chapter {chap} to CBZ format")
                shutil.rmtree(pngs_path)
                self.logger.info(f"Temporary PNGs path {pngs_path} removed")
                self.ls.update(chap)
        else:
            self.logger.info(f"Chapter {chap} already exists in CBZ format")
