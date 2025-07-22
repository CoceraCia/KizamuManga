import asyncio
from playwright.async_api import async_playwright


class ScraperBase():
    def __init__(self):
        self.browser = None
        self.context = None
    
    async def set_up(self):
        p = await async_playwright().start()
        self.browser = await p.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
    
    async def close(self):
        """
        Close the Playwright page and browser.
        """
        # Close page
        try:
            await asyncio.wait_for(self.context.close(), timeout=1)
            print("Page closed successfully")
        except Exception as e:
            print(f"⚠️ Error closing page: {type(e).__name__}: {e}")

        # Close browser
        try:
            await asyncio.wait_for(self.browser.close(), timeout=1)
            print("Browser closed successfully")
        except Exception as e:
            print(f"⚠️ Error closing browser: {e}")