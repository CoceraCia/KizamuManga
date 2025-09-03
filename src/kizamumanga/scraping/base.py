"""Base Scraper class for managing Playwright browser sessions and common validations."""

import asyncio

from playwright.async_api import async_playwright

from utils.logger import Logger


AVAILABLE_WBSITES = ["weeb_central"]


class MangaError(Exception):
    """Custom exception for manga-related errors."""


class ScraperBase:
    """Base class for manga scrapers using Playwright."""

    def __init__(self):
        """Initialize logger and browser/context placeholders."""
        self.logger = Logger("scraping.scraper_base")
        self.browser = None
        self.context = None

    async def set_up(self):
        """Start Playwright and create a headless browser context."""
        self.logger.info("Setting up Playwright browser")
        p = await async_playwright().start()
        self.logger.info("Launching headless browser")
        self.browser = await p.chromium.launch(headless=True)
        self.logger.info("Creating new browser context")
        self.context = await self.browser.new_context()

    async def close(self):
        """Safely close the browser context and browser with timeouts."""
        # Close context if initialized
        if self.context:
            try:
                await asyncio.wait_for(self.context.close(), timeout=1)
                self.logger.info("Context closed successfully")
            except Exception as e:
                self.logger.exception(f"Error closing context: {type(e).__name__}: {e}")

        # Close browser if initialized
        if self.browser:
            try:
                await asyncio.wait_for(self.browser.close(), timeout=1)
                self.logger.info("Browser closed successfully")
            except Exception as e:
                self.logger.exception(f"Error closing browser: {type(e).__name__}: {e}")

    @staticmethod
    def is_available(web: str) -> bool:
        """Check if a website is supported."""
        return web in AVAILABLE_WBSITES

    @staticmethod
    def show_available_websites():
        """Print a list of available scraper websites."""
        print("AVAILABLE WEBSITES")
        for w in AVAILABLE_WBSITES:
            print(f" - {w}")

    @staticmethod
    def get_available_websites() -> list:
        """Return a list of supported websites."""
        return AVAILABLE_WBSITES