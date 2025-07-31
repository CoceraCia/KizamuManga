"""
ArgsHandler parses and validates CLI arguments for manga downloading operations.

Supports commands for installation, search, and configuration settings (dimensions, paths, scraper, output).
"""

import argparse
import os
import re

from utils import Logger
from scraping import ScraperBase

AVAILABLE_DEVICES = {"boox_go_7":[1680, 1264]}

class ArgsHandler():
    def __init__(self):
        """Initialize the argument parser and load CLI arguments."""
        self.logger = Logger("handlers.args_handler")
        self.parser = argparse.ArgumentParser(description="Manga scrapper")
        self.subparsers = self.parser.add_subparsers(dest="command", required=True)
        self.args = self._setup_args()

    def _setup_args(self):
        """Define all command-line subcommands and parse arguments."""
        self._config_args()
        self._install_args()
        self._search_args()
        return self.parser.parse_args()

    def _install_args(self):
        """Configure CLI options for installing manga chapters."""
        install = self.subparsers.add_parser(
            "install", help="Download a manga by its name"
        )

        install.add_argument(
            "name",
            help="Name of the manga to install (e.g., 'One Piece')"
        )

        install.add_argument(
            "chap",
            nargs="?",
            help="Chapters to download. Use a number (e.g., 5) or a range (e.g., 9-18)"
        )

    def _search_args(self):
        """Configure CLI options for searching manga titles."""
        search = self.subparsers.add_parser(
            "search", help="Search for a manga by name"
        )
        search.add_argument(
            "name",
            help="The name of the manga to search (e.g., 'Bleach')"
        )

    def _config_args(self):
        """Configure CLI options for modifying configuration settings (e.g., dimensions, paths)"""
        
        config = self.subparsers.add_parser(
            "config", help="Update tool configuration settings"
        )
        conf_parser = config.add_subparsers(
            dest="conf_comm", required=True, help="Configuration category to modify"
        )

        # ---------------DIMENSIONS--------------
        conf_dimensions = conf_parser.add_parser(
            "dimensions", help="Set viewer output dimensions"
        )
        conf_dimensions.add_argument(
            "device",
            help="Optional preset device profile to auto-assign dimensions (e.g., 'kindle', 'ipad')",
            nargs="?"
        )
        conf_dimensions.add_argument(
            "--width",
            type=int,
            help="Manual width in pixels (overrides preset)"
        )
        conf_dimensions.add_argument(
            "--height",
            type=int,
            help="Manual height in pixels (overrides preset)"
        )

        # ----------------PATHS----------------------
        conf_paths = conf_parser.add_parser(
            "paths", help="Set or view download/output paths"
        )
        conf_paths.add_argument(
            "--cbz_path",
            help="Directory path where CBZ files will be stored",
        )

        # ---------------SCRAPER----------------------
        scraper = conf_parser.add_parser(
            "scraper", help="Modify scraping engine settings"
        )
        scraper.add_argument(
            "--website",
            help="Name of the manga source (e.g., 'weeb_central')"
        )
        scraper.add_argument(
            "--multiple_tasks",
            type=int,
            help="Number of parallel download tasks (e.g., 5)"
        )

        # ---------------OUTPUT----------------------
        output_img = conf_parser.add_parser(
            "output", help="Configure exported image options"
        )
        output_img.add_argument(
            "--color",
            choices=["true", "false"],
            help="Whether to keep color in exported images"
        )
        output_img.add_argument(
            "--cropping_mode",
            choices=["true", "false"],
            help="Enable automatic margin cropping for cleaner images"
        )
        

    def validate_args(self):
        """Validate argument values and perform custom preprocessing (e.g., paths, ranges)."""
        error = None
        
        match self.args.command:
            case "search":
                self.args.name = self.args.name.replace("-", " ")
            case "install":
                self.args.name = self.args.name.replace("-", " ")
                
                if self.args.chap :
                    pattern = r"^(\d+)-(\d+)$"
                    if not re.match(pattern, self.args.chap) and not self.args.chap.isdigit():
                        error = "Invalid chapters format"
                        error += "\nREMEMBER-> a single number (e.g., 5), a range (e.g., 9-18), or 'all' for all chapters"
                        self.logger.debug(
                            f"Invalid chapter range format trying to download {self.args.name}, with chapters {self.args.chap}"
                        )
                        raise ValueError("Invalid chapter format")
                    
                    chap = self.args.chap.split("-")
                    if len(chap) > 1:
                        chap[0] =  int(chap[0])
                        chap[1] = int(chap[1])
                        self.args.chap = chap
                        if (chap[0] > chap[1]):
                            error = "invalid range, firs number cannot be greater than the second one"
                    else:
                        self.args.chap = int(chap[0])

            case "config":
                if self.args.conf_comm == "dimensions":
                    if self.args.device and self.args.device not in AVAILABLE_DEVICES:
                        error = f"Invalid device, select one of these: {self._retrieve_devices()}"
                    else:
                        self.args.height = AVAILABLE_DEVICES[self.args.device][0]
                        self.args.width = AVAILABLE_DEVICES[self.args.device][1]
                
                    if self.args.width or self.args.height:
                        if self.args.width and self.args.height:
                            if self.args.width < 0:
                                error = "Invalid --width: must be a positive integer"
                            elif self.args.height < 0:
                                error = "Invalid --height: must be a positive integer"
                        else:
                            error = "You need to especify the width and height"
                            
                elif self.args.conf_comm == "paths":
                    if self.args.cbz_path:
                        new_path = os.path.abspath(self.args.cbz_path)
                        if not os.path.exists(self.args.cbz_path):
                            answer = input(f"Folder doesn't exists. Want to create one at -> {new_path} ['y','n']")
                            if answer in ("y", "n"):
                                if answer == "y":
                                    os.makedirs(new_path)
                                else:
                                    error = f"Folder doesn't exists at {new_path}"
                            else:
                                error = "No valid answer at specifying to create new path"
                        self.args.cbz_path = new_path
                            
                elif self.args.conf_comm == "scraper":
                    if self.args.website and not ScraperBase.is_available(self.args.website):
                        error = f"Invalid website: must be {ScraperBase.get_available_websites()}"

                    if self.args.multiple_tasks:
                        if self.args.multiple_tasks <= 0:
                            self.parser.error(
                            "Invalid --multiple_tasks: must be a positive integer greater than zero"
                            )
        if error:
            self.logger.error(error)
            self.parser.error(error)

    def _retrieve_devices(self):
        """Return a list of valid device names with predefined dimensions."""
        nl = []
        for i in AVAILABLE_DEVICES.keys():
            nl.append(i)
        return nl