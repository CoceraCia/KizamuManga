# -*- coding: utf-8 -*-
"""
KizamuManga - A manga downloader with support for multiple sources.
"""
import asyncio
import os
import sys
from .engine import Runner

async def main():
    await Runner().run()

def cli():
    try:
        asyncio.run(main())
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass
    finally:
        # evita ruido en stderr al cerrar
        sys.stderr = open(os.devnull, "w", encoding="utf-8")

if __name__ == "__main__":
    cli()