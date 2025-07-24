import argparse
from utils import Logger
from scraping import ScraperBase

AVAILABLE_DEVICES = {"boox_go_7":[1680, 1264]}

class ArgsHandler():
    def __init__(self):
        # INITIALIZE MAIN PARSER
        self.logger = Logger("handlers.args_handler")
        self.parser = argparse.ArgumentParser(description="Manga scrapper")
        self.subparsers = self.parser.add_subparsers(dest="command")
        self.args = self._setup_args()

    def _setup_args(self):
        self._config_args()
        self._install_args()
        self._search_args()
        return self.parser.parse_args()

    def _install_args(self):
        sub_install = self.subparsers.add_parser("install", help="install a manga by it's name")

        # INSTALL ARGS
        sub_install.add_argument("--name",
            help="Install the manga by its name (e.g., One Piece)",
            required=True)
        sub_install.add_argument("--chap",
            help="Chapters to download: a single number (e.g., 5), a range (e.g., 9-18)")

    def _search_args(self):
        sub_search = self.subparsers.add_parser("search", help="name of the manga to search")
        # SEARCH ARGS
        sub_search.add_argument("--name", help="The name of a manga", required=True)

    def _config_args(self):
        config = self.subparsers.add_parser("config", help="Update tool configuration settings")

        # ARGS
        config.add_argument(
            "--website",
            help="Target website URL where the manga scraping will take place"
        )

        config.add_argument(
            "--cbz_path",
            help="Directory path where downloaded manga CBZ files are stored"
        )

        config.add_argument(
            "--multiple_tasks",
            type=int,
            help="Number of simultaneous downloads to run in parallel"
        )
        
        # DIMENSIONS
        conf_parser = config.add_subparsers(dest="conf_comm")
        conf_dimensions = conf_parser.add_parser("dimensions", help="set dimensions for the img")
        # DIMENSIONS
        config.add_argument(
            "--device",
            help="Name of a preset device profile to automatically set image dimensions"
        )

        config.add_argument(
            "--width",
            type=int,
            help="Custom image width (used when no device preset is selected)"
        )

        config.add_argument(
            "--height",
            type=int,
            help="Custom image height (used when no device preset is selected)"
        )

    def validate_args(self):
        error = None
        if self.args.command is None:
            error = "Invalid syntaxis: must be 'search', 'install' or 'config'"

        if self.args.website is not None and not ScraperBase.is_available(self.args.website):
            error = f"Invalid website: must be {ScraperBase.get_available_websites()}"

        if self.args.multiple_tasks is not None:
            if not isinstance(self.args.multiple_tasks, int):
                self.parser.error("Invalid --multiple_tasks: must be an integer")
            elif self.args.multiple_tasks <= 0:
                self.parser.error(
                "Invalid --multiple_tasks: must be a positive integer greater than zero"
                )

        if self.args.width is not None:
            if not isinstance(self.args.width, int):
                error = "Invalid width: must be an integer"
            elif self.args.width < 0:
                error = "Invalid width: must be a positive integer"

        if self.args.height is not None:
            if not isinstance(self.args.height, int):
                self.parser.error("Invalid --height: must be an integer")
            elif self.args.height < 0:
                self.parser.error("Invalid --height: must be a positive integer")


        if error is not None:
            self.logger.error(error)
            self.parser.error(error)
