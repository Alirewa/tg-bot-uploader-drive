"""
Entry point.

Pyrogram connects via MTProto (not the HTTP Bot API), so it handles files
up to 4 GB natively — no local Bot API server is required at the library
level. The LOCAL_API_SERVER_URL variable in .env is available for operators
who also run the Docker-based local API server.
"""
import asyncio
import logging
import os
import time

# Pyrogram 2.x calls asyncio.get_event_loop() at import time via sync.py.
# Python 3.12+ no longer auto-creates an event loop outside async context,
# and Python 3.14 raises RuntimeError. Setting one explicitly before the
# import fixes the crash without affecting asyncio.run() behaviour later.
asyncio.set_event_loop(asyncio.new_event_loop())

from pyrogram import Client, idle

from config import API_HASH, API_ID, AUTO_OAUTH, BOT_TOKEN, OAUTH_SERVER_PORT
from database.session import init_db
from handlers import register_all
from services.scheduler import start_scheduler
from services.oauth_server import set_bot_app, start_oauth_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def _startup_temp_cleanup() -> None:
    """Delete all files in temp/ on startup — clears any leftovers from a crash."""
    from config import TEMP_DIR
    removed = 0
    try:
        for entry in os.scandir(TEMP_DIR):
            if entry.is_file():
                try:
                    os.unlink(entry.path)
                    removed += 1
                except Exception:
                    pass
    except Exception:
        pass
    if removed:
        logger.info("Startup: removed %d leftover temp file(s)", removed)


async def main() -> None:
    await init_db()
    _startup_temp_cleanup()

    app = Client(
        name="gdrive_uploader_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
    )

    register_all(app)
    start_scheduler()

    async with app:
        me = await app.get_me()
        logger.info("Bot started: @%s (id=%s)", me.username, me.id)
        from utils import bot_info
        bot_info.BOT_USERNAME = me.username or ""

        if AUTO_OAUTH:
            set_bot_app(app)
            await start_oauth_server(OAUTH_SERVER_PORT)
            logger.info("Auto OAuth mode active (port %d)", OAUTH_SERVER_PORT)

        await idle()


if __name__ == "__main__":
    asyncio.run(main())
