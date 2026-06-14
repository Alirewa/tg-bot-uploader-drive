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
GOOGLE_OAUTH_REDIRECT_URI: str = os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "http://localhost")

# ── Rate limiting ─────────────────────────────────────────────────────────────
RATE_LIMIT_MAX_UPLOADS: int = int(os.getenv("RATE_LIMIT_MAX_UPLOADS", "3"))
RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

# ── Temp directory ────────────────────────────────────────────────────────────
TEMP_DIR: Path = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

# ── File size limit (Pyrogram MTProto supports up to 4 GB natively) ───────────
MAX_FILE_SIZE_BYTES: int = 2 * 1024 * 1024 * 1024  # 2 GB

# ── Bot Drive (Service Account — optional shared storage) ─────────────────────
# Set BOT_DRIVE_SA_JSON to the path of your service account key JSON file.
# Leave empty to disable bot drive (users must use personal OAuth2 drive only).
BOT_DRIVE_SA_JSON: str = os.getenv("BOT_DRIVE_SA_JSON", "")
BOT_DRIVE_FOLDER_ID: str = os.getenv("BOT_DRIVE_FOLDER_ID", "")
BOT_DRIVE_MAX_GB: float = float(os.getenv("BOT_DRIVE_MAX_GB", "13.0"))
BOT_DRIVE_MAX_BYTES: int = int(BOT_DRIVE_MAX_GB * 1024 * 1024 * 1024)
CLEANUP_AFTER_HOURS: int = int(os.getenv("CLEANUP_AFTER_HOURS", "48"))

DAILY_UPLOAD_BYTES: int = int(os.getenv("DAILY_UPLOAD_BYTES", str(2 * 1024 * 1024 * 1024)))
REFERRAL_UNLOCK_COUNT: int = int(os.getenv("REFERRAL_UNLOCK_COUNT", "5"))
# Minimum seconds a user must wait between upload requests (0 = disabled)
UPLOAD_COOLDOWN_SECONDS: int = int(os.getenv("UPLOAD_COOLDOWN_SECONDS", "30"))
# Minimum seconds between any button press (anti-spam)
BTN_COOLDOWN_SECONDS: int = int(os.getenv("BTN_COOLDOWN_SECONDS", "3"))
GITHUB_URL: str = "https://github.com/Alirewa/tg-bot-uploader-drive"

# ── yt-dlp cookies (required for YouTube on VPS) ─────────────────────────────
# Path to a Netscape-format cookies.txt exported from a browser.
# Without this, YouTube blocks downloads from VPS IPs.
# See: https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp
YTDLP_COOKIES_FILE: str = os.getenv("YTDLP_COOKIES_FILE", "")

# ── Automatic OAuth callback server ───────────────────────────────────────────
# When GOOGLE_OAUTH_REDIRECT_URI is set to http://SERVER_IP:PORT/oauth/callback,
# the bot catches the code automatically — no URL copy-paste needed.
# Set OAUTH_SERVER_PORT to the port to listen on (default 8080).
# Leave GOOGLE_OAUTH_REDIRECT_URI as http://localhost to use the manual flow.
OAUTH_SERVER_PORT: int = int(os.getenv("OAUTH_SERVER_PORT", "8080"))
AUTO_OAUTH: bool = not GOOGLE_OAUTH_REDIRECT_URI.startswith("http://localhost")
