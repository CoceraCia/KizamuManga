import os
import re
from zipfile import ZipFile
from engine.logger import Logger

logger = Logger("utils.general_tools")

@staticmethod
def export_to_cbz(pngs_path, destination_path, filename):
    with ZipFile(f"{destination_path}/{filename}.zip", "w") as zipf:
        for file in sorted(os.listdir(pngs_path), key=extract_num):
            path = os.path.join(pngs_path, file)
            fname = extract_num(file)
            file = f"Page {fname:02d}.png"
            zipf.write(path, arcname=file)
    if not os.path.exists(f"{destination_path}/{filename}.cbz"):
        os.rename(
            f"{destination_path}/{filename}.zip", f"{destination_path}/{filename}.cbz"
        )
    else:
        logger.error(f"File {filename}.cbz already exists in {destination_path}")


@staticmethod
def extract_num(name):
    matches = re.findall(r"\d+", name)
    return int(matches[0]) if matches else 0