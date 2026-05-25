import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Telegram ──────────────────────────────────────────────────────────────────
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
API_ID: int = int(os.getenv("API_ID", "0"))
API_HASH: str = os.getenv("API_HASH", "")
LOCAL_API_SERVER_URL: str = os.getenv("LOCAL_API_SERVER_URL", "")

# ── Force-join channels ───────────────────────────────────────────────────────
FORCE_JOIN_CHANNELS: list[str] = [
    os.getenv("FORCE_JOIN_CHANNEL_1", "@webdw"),
    os.getenv("FORCE_JOIN_CHANNEL_2", "@webdwCF"),
]

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bot.db")

# ── Google OAuth2 (required — every user authenticates their own Drive) ────────
GOOGLE_OAUTH_CLIENT_ID: str = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_OAUTH_CLIENT_SECRET: str = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
# Users copy the full redirect URL from their browser address bar
GOOGLE_OAUTH_REDIRECT_URI: str = os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "http://localhost")

# ── Rate limiting ─────────────────────────────────────────────────────────────
RATE_LIMIT_MAX_UPLOADS: int = int(os.getenv("RATE_LIMIT_MAX_UPLOADS", "3"))
RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

# ── Temp directory ────────────────────────────────────────────────────────────
TEMP_DIR: Path = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

# ── File size limit (Pyrogram MTProto supports up to 4 GB natively) ───────────
MAX_FILE_SIZE_BYTES: int = 2 * 1024 * 1024 * 1024  # 2 GB
