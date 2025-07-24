import asyncio
from playwright.async_api import async_playwright
from utils.logger import Logger
class MangaError(Exception):
    """Custom exception for manga-related errors."""
class ScraperBase():
    def __init__(self):
        self.logger = Logger("scraping.scraper_base")
        self.browser = None
        self.context = None
    
    async def set_up(self):
        self.logger.info("Setting up Playwright browser")
        p = await async_playwright().start()
        self.logger.info("Launching headless browser")
        self.browser = await p.chromium.launch(headless=True)
        self.logger.info("Creating new browser context")
        self.context = await self.browser.new_context()
    
    async def close(self):
        """
        Close the Playwright context and browser.
        """
        # Close context
        try:
            await asyncio.wait_for(self.context.close(), timeout=1)
            self.logger.info("Context closed successfully")
        except Exception as e:
            self.logger.exception(f"Error closing page: {type(e).__name__}: {e}")

        # Close browser
        try:
            await asyncio.wait_for(self.browser.close(), timeout=1)
            self.logger.info("Browser closed successfully")
        except Exception as e:
            self.logger.exception(f"Error closing browser: {type(e).__name__}: {e}")