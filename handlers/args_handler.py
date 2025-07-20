import argparse


class ArgsHandler():
    def setup_args(self):
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