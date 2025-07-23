"""KizamuManga Engine Configuration Module"""
import os
import tempfile
import yaml

PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", ".."))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.yaml")
BASE_PNGS_PATH = tempfile.mkdtemp()
AVAILABLE_WBSITES = ["weeb_central"]


class Config:
    """Configuration class for KizamuManga engine.
        This class handles the configuration settings for the manga downloader.
    """

    def __init__(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self._config: dict = yaml.safe_load(f)
        self.cbz_path = self._config.get("cbz_path") if self._config.get(
            "cbz_path") is not None else os.path.join(PROJECT_ROOT, "manga_downloads")
        self.manga_website = self._config.get("manga_website") if self._config.get(
            "manga_website") is not None else "weeb_central"
        self.multiple_tasks: int = int(self._config.get("multiple_tasks")) if self._config.get("multiple_tasks") is not None else 5

    def set_cbz_path(self, new_path: str) -> bool:
        """Set the path for saving CBZ files."""
        if os.path.isdir(new_path):
            self._config["cbz_path"] = new_path
            self.save_data()
            return True
        else:
            print("Unable to retrieve directory, make sure that exists")
            return False

    def set_manga_website(self, new_website):
        """Set the manga website for scraping."""
        if self.manga_web_is_available(new_website):
            self._config["manga_website"] = new_website
            self.save_data()
            return True
        else:
            print("NOT AVAILABLE\nAVAILABLE WEBSITES:")
            self.show_available_websites()
            return False

    def set_mult_downloads(self, new_value):
        """Set the number of multiple tasks for downloading."""
        self._config["multiple_tasks"] = new_value
        self.save_data()

    def save_data(self):
        """Save the current configuration to the config file."""
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(self._config, f)

    def manga_web_is_available(self, name: str) -> bool:
        """Check if the given manga website is available."""
        return True if name in AVAILABLE_WBSITES else False

    def get_config_params(self):
        """Get the current configuration parameters."""
        return self._config

    @staticmethod
    def show_available_websites():
        """Display the available manga websites."""
        for i, web in enumerate(AVAILABLE_WBSITES, start=1):
            print(f"{i} -  {web}")
