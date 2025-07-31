"""Config module for loading and saving KizamuManga settings."""
import tomlkit
from .paths import CONFIG_PATH, CBZ_PATH

class Config:
    """Manages loading, updating, and saving project settings."""

    def __init__(self):
        """Load configuration from TOML file."""
        self._config = None
        self.load_toml()

    def load_toml(self):
        """Parse the TOML config file and load it into memory."""
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self._config = tomlkit.parse(f.read())

    def save_toml(self):
        """Write the current config back to the TOML file."""
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(tomlkit.dumps(self._config))

    @property
    def config(self) -> tomlkit.TOMLDocument:
        """Return the full config object."""
        return self._config

    @property
    def cropping_mode(self) -> bool:
        """Get cropping mode; default is True if unset."""
        return self.config["cropping_mode"] if self._config["cropping_mode"] != "" else True

    @cropping_mode.setter
    def cropping_mode(self, value) -> bool:
        """Set and save cropping mode."""
        self.config["cropping_mode"] = value
        self.save_toml()

    @property
    def color(self) -> bool:
        """Get color mode; default is True if unset."""
        return self.config["color"] if self._config["color"] != "" else True

    @color.setter
    def color(self, value):
        """Set and save color mode."""
        self.config["color"] = value
        self.save_toml()

    @property
    def cbz_path(self) -> str:
        """Get path for saving CBZ files; default to 'manga_downloads'."""
        return (self._config["cbz_path"] 
                if self._config["cbz_path"] != ""
                else CBZ_PATH)

    @cbz_path.setter
    def cbz_path(self, value):
        """Set and save CBZ path."""
        self._config["cbz_path"] = value
        self.save_toml()

    @property
    def website(self) -> str:
        """Get selected manga website; default is 'weeb_central'."""
        return self._config["website"] if self._config["website"] != "" else "weeb_central"

    @website.setter
    def website(self, value):
        """Set and save selected manga website."""
        self._config["website"] = value
        self.save_toml()

    @property
    def multiple_tasks(self) -> int:
        """Get max number of parallel tasks; default is 5."""
        return int(self._config["multiple_tasks"]) if self._config["multiple_tasks"] != "" else 5

    @multiple_tasks.setter
    def multiple_tasks(self, value):
        """Set and save number of parallel tasks."""
        self._config["multiple_tasks"] = value
        self.save_toml()

    @property
    def width(self) -> int:
        """Get image width; None if unset."""
        return int(self._config["width"]) if self._config["width"] != "" else None

    @width.setter
    def width(self, value):
        """Set and save image width."""
        self._config["width"] = value
        self.save_toml()

    @property
    def height(self):
        """Get image height; None if unset."""
        return int(self._config["height"]) if self._config["height"] != "" else None

    @height.setter
    def height(self, value):
        """Set and save image height."""
        self._config["height"] = value
        self.save_toml()