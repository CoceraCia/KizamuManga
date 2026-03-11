# -*- coding: utf-8 -*-
"""
KizamuManga - A manga downloader with support for multiple sources.
"""
import asyncio
import os
import sys

# if executed as a script, add 'src' to the path for relative imports to work as absolute
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

try:
    from kizamumanga.engine import Runner
except ImportError:
    # Fallback for running as a module or if the path is already configured
    from .engine import Runner

async def main():
    """Main function to run the application"""
    await Runner().run()

def cli():
    """Command line interface"""
    try:
        asyncio.run(main())
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass
    finally:
        # avoid noise in stderr when closing
        try:
            sys.stderr = open(os.devnull, "w", encoding="utf-8")
        except Exception:
            pass

if __name__ == "__main__":
    cli()
