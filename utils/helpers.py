import logging
from datetime import date as _date
from typing import Optional

from pyrogram.types import Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import ADMIN_ID, DAILY_UPLOAD_BYTES
from database.models import BotSetting, User

logger = logging.getLogger(__name__)


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
    user = await session.get(User, user_id)
    if user and user.language in ("en", "fa"):
        return user.language
    return "en"


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


def get_file_name(message: Message) -> str:
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


async def is_upload_exempt(user: User) -> bool:
    return (
        user.id == ADMIN_ID
        or bool(user.is_admin)
        or bool(user.upload_limit_exempt)
        or bool(user.referral_unlocked)
    )


async def check_and_reset_daily(session: AsyncSession, user: User) -> User:
    today = _date.today().isoformat()
    if user.daily_reset_date != today:
        user.daily_upload_bytes = 0
        user.daily_upload_count = 0
        user.daily_reset_date = today
        await session.commit()
        await session.refresh(user)
    return user


async def check_daily_limit(session: AsyncSession, user: User, file_size: int) -> tuple[bool, str]:
    if await is_upload_exempt(user):
        return False, ""
    user = await check_and_reset_daily(session, user)
    if (user.daily_upload_bytes or 0) + file_size > DAILY_UPLOAD_BYTES:
        return True, "size"
    return False, ""


async def increment_daily_usage(session: AsyncSession, user_id: int, file_size: int) -> None:
    user = await session.get(User, user_id)
    if user:
        today = _date.today().isoformat()
        if user.daily_reset_date != today:
            user.daily_upload_bytes = 0
            user.daily_upload_count = 0
            user.daily_reset_date = today
        user.daily_upload_bytes = (user.daily_upload_bytes or 0) + file_size
        user.daily_upload_count = (user.daily_upload_count or 0) + 1
        await session.commit()


async def get_referral_count(session: AsyncSession, user_id: int) -> int:
    result = await session.execute(
        select(func.count(User.id)).where(User.referred_by_id == user_id)
    )
    return result.scalar() or 0


async def get_drive_storage_info(access_token: str, refresh_token: str) -> dict:
    """
    Return storage quota dict: {limit_bytes, usage_bytes, pct, ok, error}.
    Uses the Drive about.get endpoint (accessible with drive.file scope).
    """
    import asyncio
    from services.drive_service import build_user_service
    try:
        loop = asyncio.get_event_loop()

        def _fetch():
            service, _ = build_user_service(access_token, refresh_token)
            about = service.about().get(fields="storageQuota").execute()
            return about.get("storageQuota", {})

        quota = await loop.run_in_executor(None, _fetch)
        limit = int(quota.get("limit", 0)) or (15 * 1024 ** 3)
        usage = int(quota.get("usage", 0))
        pct = min(usage / limit * 100, 100.0) if limit > 0 else 0.0
        return {"ok": True, "limit_bytes": limit, "usage_bytes": usage, "pct": pct, "error": None}
    except Exception as exc:
        return {"ok": False, "limit_bytes": 0, "usage_bytes": 0, "pct": 0, "error": str(exc)[:200]}


async def check_drive_status(access_token: str, refresh_token: str) -> dict:
    import asyncio
    from services.drive_service import build_user_service
    try:
        loop = asyncio.get_event_loop()
        service, _ = await loop.run_in_executor(
            None, lambda: build_user_service(access_token, refresh_token)
        )
        await loop.run_in_executor(
            None, lambda: service.files().list(pageSize=1, fields="files(id)").execute()
        )
        return {"ok": True, "error": None}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:300]}
