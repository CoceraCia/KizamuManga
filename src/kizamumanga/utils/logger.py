"""engine/logger.py
KizamuManga - Logger module for handling logging in the application."""

import logging
import os
from logging.handlers import RotatingFileHandler


class Logger:
    """Handles application logging with support for file and console output."""

    def __init__(self, name: str, console: bool = False):
        """Initialize logger and prepare log files and handlers."""
        project_root = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", ".."))

        self.path_logs = os.path.join(project_root, "logs")
        self.console = console
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        self._set_up_files()
        self._set_up_handlers(name)

    def _set_up_handlers(self, name: str):
        """Assign log handlers based on logger type (runner, downloader, etc.)."""
        path_handler = os.path.normpath(f"{self.path_logs}/errors.log")
        self.__add_handler(path_handler, logging.ERROR)

        if "runner" in name:
            path_handler = os.path.normpath(f"{self.path_logs}/app.log")
            self.__add_handler(path_handler, logging.DEBUG)
        elif "downloader" in name:
            path_handler = os.path.normpath(f"{self.path_logs}/downloader.log")
            self.__add_handler(path_handler, logging.INFO)
        elif "scraping" in name:
            path_handler = os.path.normpath(f"{self.path_logs}/scraping.log")
            self.__add_handler(path_handler, logging.INFO)
        if self.console:
            self.__add_handler(None, logging.DEBUG, console=True)

    def info(self, message: str):
        """Log informational messages."""
        self.logger.info(message)

    def debug(self, message: str):
        """Log debug-level messages."""
        self.logger.debug(message)

    def warning(self, message: str):
        """Log warnings."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log errors."""
        self.logger.error(message)

    def exception(self, message: str):
        """Log exceptions with traceback."""
        self.logger.error(message, exc_info=True)

    def critical(self, message: str):
        """Log critical-level errors."""
        self.logger.critical(message)

    def _set_up_files(self):
        """Ensure log directory and default log files exist."""
        os.makedirs(self.path_logs, exist_ok=True)

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

    def __add_handler(self, path_handler, level, console=False):
        """Add a logging handler for file or console output."""
        formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if console:
            handler = logging.StreamHandler()
        else:
            handler = RotatingFileHandler(path_handler, maxBytes=5_000_000, backupCount=3, delay=True)
        handler.setLevel(level)
        handler.setFormatter(formater)
        self.logger.addHandler(handler)