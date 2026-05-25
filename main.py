"""
Entry point.

Pyrogram connects via MTProto (not the HTTP Bot API), so it handles files
up to 4 GB natively — no local Bot API server is required at the library
level. The LOCAL_API_SERVER_URL variable in .env is available for operators
who also run the Docker-based local API server.
"""
import asyncio
import logging

from pyrogram import Client, idle

from config import API_HASH, API_ID, BOT_TOKEN
from database.session import init_db
from handlers import register_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    await init_db()

    app = Client(
        name="gdrive_uploader_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
    )

    register_all(app)

    async with app:
        me = await app.get_me()
        logger.info("Bot started: @%s (id=%s)", me.username, me.id)
        await idle()


if __name__ == "__main__":
    asyncio.run(main())
