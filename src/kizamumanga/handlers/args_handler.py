import argparse
import re
from utils import Logger
from scraping import ScraperBase

AVAILABLE_DEVICES = {"boox_go_7":[1680, 1264]}

class ArgsHandler():
    def __init__(self):
        # INITIALIZE MAIN PARSER
        self.logger = Logger("handlers.args_handler")
        self.parser = argparse.ArgumentParser(description="Manga scrapper")
        self.subparsers = self.parser.add_subparsers(dest="command", required=True)
        self.args = self._setup_args()

    def _setup_args(self):
        self._config_args()
        self._install_args()
        self._search_args()
        return self.parser.parse_args()

    def _install_args(self):
        install = self.subparsers.add_parser("install", help="install a manga by it's name")

        # INSTALL ARGS
        install.add_argument("name",
            help="Install the manga by its name (e.g., One Piece)")
        install.add_argument("chap",
            help="Chapters to download: a single number (e.g., 5), a range (e.g., 9-18)",
            nargs="?")

    def _search_args(self):
        sub_search = self.subparsers.add_parser("search", help="name of the manga to search")
        # SEARCH ARGS
        sub_search.add_argument("name", help="The name of a manga")

    def _config_args(self):
        config = self.subparsers.add_parser("config", help="Update tool configuration settings")
        conf_parser = config.add_subparsers(dest="conf_comm", required=True)

        # ----------------GENERAL ARGS------------
        conf_gen = conf_parser.add_parser("general", help="General configuration setting")
        conf_gen.add_argument(
            "--website",
            help="Target website URL where the manga scraping will take place"
        )

        conf_gen.add_argument(
            "--color",
            help="Define 'true' if wanted to export image with color else grayscale will be applied"
        )

        conf_gen.add_argument(
            "--cbz_path",
            help="Directory path where downloaded manga CBZ files are stored"
        )

        conf_gen.add_argument(
            "--multiple_tasks",
            type=int,
            help="Number of simultaneous downloads to run in parallel"
        )
        
        # ---------------DIMENSIONS--------------
        conf_dimensions = conf_parser.add_parser("dimensions", help="set dimensions for the img")
        
        conf_dimensions.add_argument(
            "device",
            help="Name of a preset device profile to automatically set image dimensions",
            nargs="?"
        )

        conf_dimensions.add_argument(
            "--width",
            type=int,
            help="Custom image width (used when no device preset is selected)"
        )

        conf_dimensions.add_argument(
            "--height",
            type=int,
            help="Custom image height (used when no device preset is selected)"
        )

    def validate_args(self):
        error = None
        match self.args.command:
            case "install" | "search":
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
                else:
                    if self.args.color:
                        if self.args.color.lower() in ("yes", "y", "true", "1"):
                            self.args.color = True
                        elif self.args.color.lower() in ("no", "n", "false", "0"):
                            self.args.color = False
                    if self.args.website and not ScraperBase.is_available(self.args.website):
                        error = f"Invalid website: must be {ScraperBase.get_available_websites()}"

                    if self.args.multiple_tasks:
                        if not isinstance(self.args.multiple_tasks, int):
                            self.parser.error("Invalid --multiple_tasks: must be an integer")
                        elif self.args.multiple_tasks <= 0:
                            self.parser.error(
                            "Invalid --multiple_tasks: must be a positive integer greater than zero"
                            )
        if error:
            self.logger.error(error)
            self.parser.error(error)

    def _retrieve_devices(self):
        nl = []
        for i in AVAILABLE_DEVICES.keys():
            nl.append(i)
        return nl