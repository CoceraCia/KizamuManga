"""engine/logger.py
KizamuManga - Logger module for handling logging in the application."""
import logging
import os
from .config import PROJECT_ROOT

class Logger:
    """Logger class to handle logging for the application."""
    def __init__(self, name: str, console: bool = False):
        self.path_logs = os.path.join(PROJECT_ROOT, "logs")
        os.makedirs(os.path.dirname("logs/"), exist_ok=True)
        self.console = console
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self._set_up_files()
        self._set_up_handlers(name)


    def _set_up_handlers(self, name: str ):
        """Set up logging handlers for different log files."""
        formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        errors_handler = logging.FileHandler(f"{self.path_logs}/errors.log")
        errors_handler.setLevel(logging.ERROR)
        errors_handler.setFormatter(formater)
        self.logger.addHandler(errors_handler)

        if "runner" in name:
            app_handler = logging.FileHandler(f"{self.path_logs}/app.log")
            app_handler.setLevel(logging.DEBUG)
            app_handler.setFormatter(formater)
            self.logger.addHandler(app_handler)
        elif "downloader" in name:
            downloader_handler = logging.FileHandler(f"{self.path_logs}/downloader.log")
            downloader_handler.setLevel(logging.INFO)
            downloader_handler.setFormatter(formater)
            self.logger.addHandler(downloader_handler)
        elif "scraping" in name:
            scraping_handler = logging.FileHandler(f"{self.path_logs}/scraping.log")
            scraping_handler.setLevel(logging.INFO)
            scraping_handler.setFormatter(formater)
            self.logger.addHandler(scraping_handler)
        if self.console:
            # Add console handler for debugging
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formater)
            self.logger.addHandler(console_handler)

    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)

    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)

    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)

    def critical(self, message: str):
        """Log a critical message."""
        self.logger.critical(message)


    def _set_up_files(self):
        """Create log directory and files if they do not exist."""
        os.makedirs(self.path_logs, exist_ok=True)

        # Create log files if they do not exist
        app_log = f"{self.path_logs}/app.log"
        if not os.path.exists(app_log):
            with open(app_log, "w", encoding="utf-8"):
                pass

        downloader_log = f"{self.path_logs}/downloader.log"
        if not os.path.exists(downloader_log):
            with open(downloader_log, "w", encoding="utf-8"):
                pass

        errors_log = f"{self.path_logs}/errors.log"
        if not os.path.exists(errors_log):
            with open(errors_log, "w", encoding="utf-8"):
                pass

        scraping_log = f"{self.path_logs}/scraping.log"
        if not os.path.exists(scraping_log):
            with open(scraping_log, "w", encoding="utf-8"):
                pass
