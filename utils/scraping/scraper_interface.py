from abc import ABC, abstractmethod


class ScraperInterface(ABC):
    @abstractmethod
    async def set_up(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def get_mangas_by_title(self, title):
        pass

    @abstractmethod
    async def get_chapters_by_mangaurl(self, manga_url):
        pass

    @abstractmethod
    async def obtain_chapter_content(self, manga_url):
        pass
