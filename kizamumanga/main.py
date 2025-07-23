import asyncio
import os
import sys
from core import Runner
from core import MangaError, ChapterNotFoundError, InvalidChapterRangeError, ScraperConnectionError

async def main():
    await Runner().run()
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (asyncio.exceptions.CancelledError, KeyboardInterrupt):
        pass
    finally:
        sys.stderr = open(os.devnull, "w")
