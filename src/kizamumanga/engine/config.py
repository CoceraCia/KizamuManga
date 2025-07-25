"""Config module for loading and saving KizamuManga settings."""

import os
import tempfile
import yaml

PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", ".."))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.yaml")
BASE_PNGS_PATH = tempfile.mkdtemp()


class Config:
    """Configuration manager for KizamuManga engine."""

    def __init__(self):
        """Initialize config by loading from YAML file."""
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self._config: dict = yaml.safe_load(f)
        self._cbz_path = None
        self._manga_website = None
        self._multiple_tasks = None
        self._width = None
        self._height = None

    def get_cbz_path(self):
        """Get path for storing CBZ files."""
        return self._config.get("cbz_path") or os.path.join(PROJECT_ROOT, "manga_downloads")

    def set_cbz_path(self, new_path: str):
        """Set path for CBZ files and save."""
        if os.path.isdir(new_path):
            self._cbz_path = new_path
            self._config["cbz_path"] = new_path
            self.save_data()
        else:
            raise ValueError("Directory does not exist")

    def get_manga_website(self):
        """Get selected manga website."""
        return self._config.get("manga_website") or "weeb_central"

    def set_manga_website(self, new_website):
        """Set manga website and save."""
        self._config["manga_website"] = new_website
        self.save_data()

    def get_multiple_tasks(self):
        """Get configured number of concurrent tasks."""
        return self._config.get("multiple_tasks") or 5

    def set_multiple_tasks(self, new_value: int):
        """Set number of concurrent tasks and save."""
        self._config["multiple_tasks"] = new_value
        self.save_data()

    def get_width(self):
        """Get configured image width."""
        return self._config.get("width")

    def set_width(self, value):
        """Set image width and save."""
        self._config["width"] = value
        self.save_data()

    def get_height(self):
        """Get configured image height."""
        return self._config.get("height")

    def set_height(self, value):
        """Set image height and save."""
        self._config["height"] = value
        self.save_data()

    def save_data(self):
        """Save current config to YAML file."""
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(self._config, f)

    def get_config_params(self):
        """Return entire config dictionary."""
        return self._config
