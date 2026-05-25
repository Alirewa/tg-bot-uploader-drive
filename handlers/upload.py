"""
File upload handler — personal Google Drive (OAuth2) only.

Flow:
  1. File received → gate checks (bot status, force-join, rate-limit, size)
  2. If not authenticated → show mandatory auth prompt
  3. Download from Telegram with live progress bar
  4. Upload to user's personal Google Drive with live progress bar
  5. Return shareable link
"""
import asyncio
import logging
import os
import tempfile

from pyrogram import Client, filters
from pyrogram.types import Message

from config import ADMIN_ID, MAX_FILE_SIZE_BYTES
from database.models import Upload, User as UserModel
from database.session import AsyncSessionLocal
from services.drive_service import build_user_service, sync_upload
from services.force_join import get_unjoined_channels
from services.rate_limiter import check_rate_limit, update_rate_limit
from utils.helpers import get_file_name, get_file_size, get_or_create_user, get_setting, get_user_lang
from utils.keyboards import authenticate_button, back_to_main, force_join, main_menu
from utils.progress import ProgressBar, format_bytes
from utils.state import currently_uploading, user_states
from utils.strings import t

logger = logging.getLogger(__name__)


def register(app: Client) -> None:

    @app.on_message(
        filters.private
        & (
            filters.document
            | filters.video
            | filters.audio
            | filters.animation
            | filters.photo
            | filters.voice
            | filters.video_note
        )
    )
    async def on_file(client: Client, message: Message):
        user_id = message.from_user.id

        # ── Bot status ──────────────────────────────────────────────────────────
        async with AsyncSessionLocal() as session:
            bot_status = await get_setting(session, "bot_status", "on")
            lang = await get_user_lang(session, user_id)

        if bot_status == "off" and user_id != ADMIN_ID:
            await message.reply(t("bot_offline", lang))
            return

        # ── Force join ──────────────────────────────────────────────────────────
        unjoined = await get_unjoined_channels(client, user_id)
        if unjoined:
            await message.reply(
                t("force_join_prompt", lang),
                reply_markup=force_join(unjoined, lang),
            )
            return

        # ── Concurrent upload guard ─────────────────────────────────────────────
        if user_id in currently_uploading:
            await message.reply(t("upload_already_running", lang))
            return

        # ── Rate limit ──────────────────────────────────────────────────────────
        limited, wait_secs = await check_rate_limit(user_id)
        if limited:
            await message.reply(t("upload_rate_limited", lang).format(wait=wait_secs))
            return

        # ── File size ───────────────────────────────────────────────────────────
        file_size = get_file_size(message)
        if file_size and file_size > MAX_FILE_SIZE_BYTES:
            await message.reply(
                t("upload_too_large", lang).format(size=format_bytes(file_size))
            )
            return

        # ── Mandatory OAuth gate ────────────────────────────────────────────────
        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(session, message.from_user)
            has_drive = user.has_personal_drive

        if not has_drive:
            await message.reply(
                t("auth_required", lang),
                reply_markup=authenticate_button(lang),
            )
            return

        # ── All checks passed — begin upload ────────────────────────────────────
        await _start_upload(client, message, user_id, lang)


async def _start_upload(client: Client, message: Message, user_id: int, lang: str) -> None:
    """Orchestrates download → Drive upload → DB record → result message."""
    currently_uploading.add(user_id)
    await update_rate_limit(user_id)

    file_name = get_file_name(message)
    file_size = get_file_size(message) or 0
    status_msg = await message.reply(t("upload_starting", lang))
    temp_path: str | None = None

    try:
        # ── 1. Download from Telegram ───────────────────────────────────────────
        with tempfile.NamedTemporaryFile(delete=False, dir="temp", suffix=f"_{file_name}") as tmp:
            temp_path = tmp.name

        dl_bar = ProgressBar(file_size)

        async def on_dl(current: int, total: int) -> None:
            if dl_bar.should_update():
                try:
                    await status_msg.edit_text(
                        dl_bar.render(current, t("download_header", lang))
                    )
                except Exception:
                    pass

        await message.download(file_name=temp_path, progress=on_dl)
        actual_size = os.path.getsize(temp_path)

        # ── 2. Build Drive service (refresh token if needed) ────────────────────
        async with AsyncSessionLocal() as session:
            user = await session.get(UserModel, user_id)

        service, new_token = build_user_service(
            user.oauth_access_token, user.oauth_refresh_token
        )

        # Persist refreshed token if it changed
        if new_token != user.oauth_access_token:
            async with AsyncSessionLocal() as session:
                u = await session.get(UserModel, user_id)
                if u:
                    u.oauth_access_token = new_token
                    await session.commit()

        # ── 3. Upload to Google Drive ───────────────────────────────────────────
        up_bar = ProgressBar(actual_size)
        loop = asyncio.get_event_loop()

        async def on_up(current: int, total: int) -> None:
            if up_bar.should_update():
                try:
                    await status_msg.edit_text(
                        up_bar.render(current, t("upload_header", lang))
                    )
                except Exception:
                    pass

        file_id, share_link = await loop.run_in_executor(
            None, sync_upload, temp_path, file_name, service, on_up, loop
        )

        # ── 4. Persist upload record ────────────────────────────────────────────
        async with AsyncSessionLocal() as session:
            session.add(Upload(
                user_id=user_id,
                service_account_id=None,
                gdrive_file_id=file_id,
                file_name=file_name,
                file_size_bytes=actual_size,
                share_link=share_link,
                is_personal_drive=True,
            ))
            await session.commit()

        # ── 5. Send result ──────────────────────────────────────────────────────
        await status_msg.edit_text(
            t("upload_complete", lang).format(
                name=file_name,
                size=format_bytes(actual_size),
                link=share_link,
            ),
            disable_web_page_preview=True,
        )

    except Exception:
        logger.exception("Upload failed for user %s", user_id)
        try:
            await status_msg.edit_text(t("upload_failed", lang))
        except Exception:
            pass

    finally:
        currently_uploading.discard(user_id)
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass
