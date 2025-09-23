# kizamumanga/main.py
# -*- coding: utf-8 -*-
"""
KizamuManga - A manga downloader
with support for multiple sources.
"""
import asyncio
import os
import sys
from .engine import Runner

async def main():
    await Runner().run()
 
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (asyncio.exceptions.CancelledError, KeyboardInterrupt) as e:
        pass
    finally:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")
