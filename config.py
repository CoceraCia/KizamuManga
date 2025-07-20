import tempfile
import json

with open("config.json", "r", encoding="utf-8") as f:
    config: dict = json.load(f)
PNGS_PATH = tempfile.mkdtemp()
CBZ_PATH = config.get("cbz_path")
MANGA_WEBSITE = config.get("manga_website")