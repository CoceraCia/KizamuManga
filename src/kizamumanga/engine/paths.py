import os
import tomlkit

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.toml")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = tomlkit.parse(f.read())

CBZ_PATH = config["cbz_path"] if config["cbz_path"] != "" else os.path.join(PROJECT_ROOT, "manga_downloads")
TEMP_PATH = os.path.join(CBZ_PATH, ".kizamumanga")