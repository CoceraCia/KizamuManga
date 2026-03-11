# -*- coding: utf-8 -*-
"""
KizamuManga - A manga downloader with support for multiple sources.
Entry point: handles CLI startup and graceful shutdown.
"""

import asyncio
import os
import sys


def _setup_path() -> None:
    """Ensure the package root is on sys.path when run as a script."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)


def _import_runner():
    """Import Runner, setting up the path first if needed."""
    _setup_path()
    try:
        from kizamumanga.engine import Runner
    except ImportError:
        from .engine import Runner  # fallback when used as a package
    return Runner


async def main() -> None:
    Runner = _import_runner()
    await Runner().run()


def cli() -> None:
    """Command-line entry point with graceful shutdown handling."""
    try:
        asyncio.run(main())
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass  # Clean exit on Ctrl+C — no traceback needed
    finally:
        _silence_stderr()


def _silence_stderr() -> None:
    """Redirect stderr to /dev/null to suppress shutdown noise."""
    try:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")
    except Exception:
        pass  # If this fails, it's not worth crashing over


if __name__ == "__main__":
    cli()