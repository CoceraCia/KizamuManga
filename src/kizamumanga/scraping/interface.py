"""Abstract interface defining required methods for manga scrapers."""

from abc import ABC, abstractmethod


class ScraperInterface(ABC):
    """Interface for scraper classes to standardize manga data retrieval."""

    @abstractmethod
    async def set_up(self):
        """Initialize the scraper, e.g., browser or session setup."""
        pass

    @abstractmethod
    async def close(self):
        """Cleanly close any open sessions or browser contexts."""
        pass

    @abstractmethod
    async def get_mangas_by_title(self, title) -> dict:
        """Retrieve manga search results by title."""
        pass

    @abstractmethod
    async def get_chapters_by_mangaurl(self, manga_url) -> dict:
        """Retrieve available chapters for a given manga URL."""
        pass

    @abstractmethod
    async def obtain_chapter_content(self, manga_url) -> dict:
        """Obtain all image URLs for a given chapter."""
        pass
