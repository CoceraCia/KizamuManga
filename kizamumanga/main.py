import asyncio
import os
import sys
from app_runner import AppRunner

async def main():
    await AppRunner().run()
    
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (asyncio.exceptions.CancelledError, KeyboardInterrupt):
        pass
    finally:
        sys.stderr = open(os.devnull, "w")
