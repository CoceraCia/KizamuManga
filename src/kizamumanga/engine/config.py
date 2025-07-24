import os
import tempfile
import yaml

PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", ".."))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.yaml")
BASE_PNGS_PATH = tempfile.mkdtemp()
AVAILABLE_WBSITES = ["weeb_central"]


class Config:
    """Configuration class for KizamuManga engine."""

    def __init__(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self._config: dict = yaml.safe_load(f)
        self._cbz_path = None
        self._manga_website = None
        self._multiple_tasks = None
        self._width = None
        self._height = None

    def get_cbz_path(self):
        return self._config.get("cbz_path") or os.path.join(PROJECT_ROOT, "manga_downloads")

    def set_cbz_path(self, new_path: str):
        if os.path.isdir(new_path):
            self._cbz_path = new_path
            self._config["cbz_path"] = new_path
            self.save_data()
        else:
            raise ValueError("Directory does not exist")

    def get_manga_website(self):
        return self._config.get("manga_website") or "weeb_central"

    def set_manga_website(self, new_website):
        if new_website in AVAILABLE_WBSITES:
            self._manga_website = new_website
            self.save_data()
        else:
            raise ValueError(f"Website not available. Choose from: {AVAILABLE_WBSITES}")

    def get_multiple_tasks(self):
        return self._config.get("multiple_tasks") or 5

    def set_multiple_tasks(self, new_value:int):
        if isinstance(new_value, int) and new_value > 0:
            self._multiple_tasks = new_value
            self.save_data()
        else:
            raise ValueError("multiple_tasks must be a positive integer")

    def get_width(self):
        return self._config.get("width")

    def set_width(self, value):
        if isinstance(value, int) and value > 0:
            self._width = value
        else:
            raise ValueError("Width must be a positive integer")

    def get_height(self):
        return self._config.get("height")

    def set_height(self, value):
        if isinstance(value, int) and value > 0:
            self._height = value
        else:
            raise ValueError("Height must be a positive integer")

    def save_data(self):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(self._config, f)

    def get_config_params(self):
        return self._config

    @staticmethod
    def show_available_websites():
        for i, web in enumerate(AVAILABLE_WBSITES, start=1):
            print(f"{i} -  {web}")
