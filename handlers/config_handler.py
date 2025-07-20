import tempfile
import yaml

AVAILABLE_WBSITES = ["weeb_central"]
BASE_PNGS_PATH = tempfile.mkdtemp()

class ConfigHandler:
    def __init__(self):
        with open("config.yaml", "r", encoding="utf-8") as f:
            self._config: dict = yaml.safe_load(f)
        self.cbz_path = self._config.get("cbz_path")
        self.manga_website = self._config.get("manga_website")

    @staticmethod
    def manga_web_is_available(name: str) -> bool:
        return True if name in AVAILABLE_WBSITES else False

    @staticmethod
    def show_available_websites():
        for i, web in enumerate(AVAILABLE_WBSITES, start=1):
            print(f"{i} -  {web}")
