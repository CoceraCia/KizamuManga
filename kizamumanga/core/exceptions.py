# core/exceptions.py

class MangaError(Exception):
    """Base error for all manga downloader exceptions"""
    pass

class ChapterNotFoundError(MangaError):
    """Raised when the selected chapter is not found"""
    pass

class InvalidChapterRangeError(MangaError):
    """Raised when chapter range format is invalid"""
    pass

class ScraperConnectionError(MangaError):
    """Raised when scraper fails to connect or retrieve data"""
    pass

class IncorrectScraper(MangaError):
    """Raised when scraper fails to connect or retrieve data"""
    pass
