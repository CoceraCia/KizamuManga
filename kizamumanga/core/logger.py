import logging
import os

class Logger:
    def __init__(self, name: str):
        os.makedirs(os.path.dirname("kizamumanga/logs/"), exist_ok=True)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.__set_up_files()
        self.__set_up_handlers()
        
        
    def __set_up_handlers(self):
        formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        app_handler = logging.FileHandler("kizamumanga/logs/app.log")
        app_handler.setLevel(logging.DEBUG)
        
        app_handler.setFormatter(formater)
        self.logger.addHandler(app_handler)
        
        downloader_handler = logging.FileHandler("kizamumanga/logs/downloader.log")
        downloader_handler.setLevel(logging.INFO)
        downloader_handler.setFormatter(formater)
        self.logger.addHandler(downloader_handler)
        
        errors_handler = logging.FileHandler("kizamumanga/logs/errors.log")
        errors_handler.setLevel(logging.ERROR)
        errors_handler.setFormatter(formater)
        self.logger.addHandler(errors_handler)
        
        scraping_handler = logging.FileHandler("kizamumanga/logs/scraping.log")
        scraping_handler.setLevel(logging.INFO)
        scraping_handler.setFormatter(formater)
        self.logger.addHandler(scraping_handler)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formater)
        self.logger.addHandler(console_handler)
        
    def info(self, message: str):
        self.logger.info(message)
        
    def debug(self, message: str):
        self.logger.debug(message)
        
    def warning(self, message: str):
        self.logger.warning(message)
        
    def error(self, message: str):
        self.logger.error(message)
        
    def critical(self, message: str):
        self.logger.critical(message)
        

    def __set_up_files(self):
        os.makedirs("kizamumanga/logs/", exist_ok=True)
        
        # Create log files if they do not exist
        app_log = "kizamumanga/logs/app.log"
        if not os.path.exists(app_log):
            with open(app_log, "w") as f:
                pass

        downloader_log = "kizamumanga/logs/downloader.log"
        if not os.path.exists(downloader_log):
            with open(downloader_log, "w") as f:
                pass

        errors_log = "kizamumanga/logs/errors.log"
        if not os.path.exists(errors_log):
            with open(errors_log, "w") as f:
                pass

        scraping_log = "kizamumanga/logs/scraping.log"
        if not os.path.exists(scraping_log):
            with open(scraping_log, "w") as f:
                pass