import logging
from typing import Optional

from pyrogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import BotSetting, User

logger = logging.getLogger(__name__)


# ── User helpers ──────────────────────────────────────────────────────────────

async def get_or_create_user(session: AsyncSession, tg_user) -> User:
    user = await session.get(User, tg_user.id)
    if not user:
        user = User(
            id=tg_user.id,
            username=getattr(tg_user, "username", None),
            first_name=getattr(tg_user, "first_name", "") or "",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def get_user_lang(session: AsyncSession, user_id: int) -> str:
    """Return the user's stored language preference, defaulting to 'en'."""
    user = await session.get(User, user_id)
    if user and user.language in ("en", "fa"):
        return user.language
    return "en"


# ── Bot setting helpers ───────────────────────────────────────────────────────

async def get_setting(session: AsyncSession, key: str, default: str = "") -> str:
    setting = await session.get(BotSetting, key)
    return setting.value if setting else default


async def set_setting(session: AsyncSession, key: str, value: str) -> None:
    setting = await session.get(BotSetting, key)
    if setting:
        setting.value = value
    else:
        session.add(BotSetting(key=key, value=value))
    await session.commit()


# ── File metadata helpers ─────────────────────────────────────────────────────

def get_file_name(message: Message) -> str:
    """Extract a sensible filename from any media message."""
    if message.document:
        return message.document.file_name or f"document_{message.document.file_unique_id}"
    if message.video:
        return message.video.file_name or f"video_{message.video.file_unique_id}.mp4"
    if message.audio:
        return message.audio.file_name or f"audio_{message.audio.file_unique_id}.mp3"
    if message.animation:
        return message.animation.file_name or f"animation_{message.animation.file_unique_id}.mp4"
    if message.photo:
        return f"photo_{message.photo.file_unique_id}.jpg"
    if message.voice:
        return f"voice_{message.voice.file_unique_id}.ogg"
    if message.video_note:
        return f"videonote_{message.video_note.file_unique_id}.mp4"
    return "unknown_file"


def get_file_size(message: Message) -> Optional[int]:
    """Return file size in bytes, or None if unavailable."""
    for attr in ("document", "video", "audio", "animation", "photo", "voice", "video_note"):
        media = getattr(message, attr, None)
        if media:
            return getattr(media, "file_size", None)
    return None


def has_media(message: Message) -> bool:
    return any(
        getattr(message, attr, None)
        for attr in ("document", "video", "audio", "animation", "photo", "voice", "video_note")
    )
