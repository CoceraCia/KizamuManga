"""Config module for loading and saving KizamuManga settings."""

import os
import tempfile
import tomlkit

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.toml")


class Config:
    """Configuration manager for KizamuManga engine."""

    def __init__(self):
        """Initialize config by loading from YAML file."""
        self._config = None
        self.load_toml()

    def load_toml(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self._config = tomlkit.parse(f.read())

    def save_toml(self):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(tomlkit.dumps(self._config))

    # -----------PROPERTIES------------
    @property
    def config(self) -> tomlkit.TOMLDocument:
        return self._config

    # ------------cbz_path---------------
    @property
    def cbz_path(self) -> str:
        return (
            self._config["cbz_path"]
            if self._config["cbz_path"] != ""
            else os.path.join(PROJECT_ROOT, "manga_downloads")
        )

    @cbz_path.setter
    def cbz_path(self, value):
        self._config["cbz_path"] = value
        self.save_toml()

    # ------------manga_website-----------
    @property
    def manga_website(self) -> str:
        return (
            self._config["manga_website"]
            if self._config["manga_website"] != ""
            else "weeb_central"
        )

    @manga_website.setter
    def manga_website(self, value):
        self._config["manga_website"] = value
        self.save_toml()

    # -----------multiple_tasks-----------
    @property
    def multiple_tasks(self) -> int:
        return (
            int(self._config["multiple_tasks"])
            if self._config["multiple_tasks"] != ""
            else 5
        )

    @multiple_tasks.setter
    def multiple_tasks(self, value):
        self._config["multiple_tasks"] = value
        self.save_toml()

    # -------------width-------------
    @property
    def width(self) -> int:
        return int(self._config["width"]) if self._config["width"] != "" else None

    @width.setter
    def width(self, value):
        self._config["width"] = value
        self.save_toml()

    # ----------height----------------
    @property
    def height(self):
        return int(self._config["height"]) if self._config["height"] != "" else None

    @height.setter
    def height(self, value):
        self._config["height"] = value
        self.save_toml()
