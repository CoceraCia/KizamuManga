import os
import tempfile
import yaml

AVAILABLE_WBSITES = ["weeb_central"]
BASE_PNGS_PATH = tempfile.mkdtemp()

class Config:
    def __init__(self):
        with open("kizamumanga/core/config.yaml", "r", encoding="utf-8") as f:
            self._config: dict = yaml.safe_load(f)
        self.cbz_path = self._config.get("cbz_path")
        self.manga_website = self._config.get("manga_website")
        self.multiple_tasks:int = int(self._config.get("multiple_tasks"))
        
        
    def set_cbz_path(self, new_path:str)->bool:
        if os.path.isdir(new_path):
            self._config["cbz_path"] = new_path
            self.save_data()
            return True
        else:
            print("Unable to retrieve directory, make sure that exists")
            return False
        
    def set_manga_website(self, new_website):
        if self.manga_web_is_available(new_website):
            self._config["manga_website"] = new_website
            self.save_data()
            return True
        else:
            print("NOT AVAILABLE\nAVAILABLE WEBSITES:")
            self.show_available_websites()
            return False
        
    def set_mult_downloads(self, new_value):
        self._config["multiple_tasks"] = new_value
        self.save_data()
    
    def save_data(self):
        with open("kizamumanga/core/config.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(self._config, f)
            
    def manga_web_is_available(self, name: str) -> bool:
        return True if name in AVAILABLE_WBSITES else False

    @staticmethod
    def show_available_websites():
        for i, web in enumerate(AVAILABLE_WBSITES, start=1):
            print(f"{i} -  {web}")
