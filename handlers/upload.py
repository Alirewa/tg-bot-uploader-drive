import asyncio
import logging
import os
import re
import time
import tempfile

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message
from sqlalchemy import func, select

from config import (
    ADMIN_ID,
    BOT_DRIVE_FOLDER_ID,
    BOT_DRIVE_MAX_BYTES,
    BOT_DRIVE_SA_JSON,
    MAX_FILE_SIZE_BYTES,
    UPLOAD_COOLDOWN_SECONDS,
)
from database.models import Upload, User as UserModel
from database.session import AsyncSessionLocal
from services.drive_service import build_bot_service, build_user_service, sync_upload
from services.force_join import get_unjoined_channels
from services.rate_limiter import check_rate_limit, update_rate_limit
from utils.helpers import (
    check_daily_limit,
    get_file_name,
    get_file_size,
    get_or_create_user,
    get_setting,
    get_user_lang,
    increment_daily_usage,
    is_upload_exempt,
)
from utils.keyboards import authenticate_button, back_to_main, dest_selection, drive_selection, force_join, main_menu, referral_menu, yt_quality_menu
from utils.progress import ProgressBar, format_bytes
from services.downloader import download_direct, download_gdrive, download_url, download_via_cobalt, detect_source, extract_gdrive_id, source_icon
from utils.state import (
    UserState, currently_uploading, pending_uploads, upload_cooldowns, user_states,
)
from utils.strings import t

logger = logging.getLogger(__name__)

_FILE_FILTER = (
    filters.document
    | filters.video
    | filters.audio
    | filters.animation
    | filters.photo
    | filters.voice
    | filters.video_note
)


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_bot_drive_used() -> int:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(func.sum(Upload.file_size_bytes)).where(
                Upload.is_personal_drive.is_(False),
                Upload.is_deleted.is_(False),
            )
        )
        return result.scalar() or 0


def _check_cooldown(user_id: int) -> int:
    """Return remaining cooldown seconds, or 0 if allowed."""
    last = upload_cooldowns.get(user_id, 0)
    remaining = UPLOAD_COOLDOWN_SECONDS - (time.time() - last)
    return max(0, int(remaining) + 1) if remaining > 0 else 0


async def _common_guards(
    client: Client,
    message: Message,
    user_id: int,
    lang: str,
) -> bool:
    """
    Run bot-status / force-join / concurrent / rate-limit checks.
    Returns True if the request should be blocked.
    """
    async with AsyncSessionLocal() as session:
        bot_status = await get_setting(session, "bot_status", "on")

    if bot_status == "off" and user_id != ADMIN_ID:
        await message.reply(t("bot_offline", lang))
        return True

    unjoined = await get_unjoined_channels(client, user_id)
    if unjoined:
        await message.reply(t("force_join_prompt", lang), reply_markup=force_join(unjoined, lang))
        return True

    if user_id in currently_uploading:
        await message.reply(t("upload_already_running", lang))
        return True

    limited, wait_secs = await check_rate_limit(user_id)
    if limited:
        await message.reply(t("upload_rate_limited", lang).format(wait=wait_secs))
        return True

    return False


# ── Register ──────────────────────────────────────────────────────────────────

def register(app: Client) -> None:

    # ── Telegram media files ───────────────────────────────────────────────────

    @app.on_message(filters.private & _FILE_FILTER)
    async def on_file(client: Client, message: Message):
        user_id = message.from_user.id

        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)

        if await _common_guards(client, message, user_id, lang):
            return

        file_size = get_file_size(message)
        if file_size and file_size > MAX_FILE_SIZE_BYTES:
            await message.reply(t("upload_too_large", lang).format(size=format_bytes(file_size)))
            return

        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(session, message.from_user)
            has_drive   = user.has_personal_drive
            exempt      = await is_upload_exempt(user)
            limited, reason = await check_daily_limit(session, user, file_size or 0)

        if limited:
            key = "daily_limit_count" if reason == "count" else "daily_limit_size"
            await message.reply(t(key, lang), reply_markup=referral_menu(lang))
            return

        if not exempt:
            secs = _check_cooldown(user_id)
            if secs:
                await message.reply(t("upload_cooldown", lang).format(seconds=secs))
                return

        if not BOT_DRIVE_SA_JSON:
            if not has_drive:
                await message.reply(t("auth_required", lang), reply_markup=authenticate_button(lang))
                return
            upload_cooldowns[user_id] = time.time()
            await _start_upload(client, message, user_id, lang, use_bot_drive=False)
            return

        bot_used = await _get_bot_drive_used()
        bot_full = (file_size or 0) + bot_used > BOT_DRIVE_MAX_BYTES

        upload_cooldowns[user_id] = time.time()
        pending_uploads[user_id] = message
        user_states[user_id]     = UserState.PENDING_DRIVE_SELECTION

        await message.reply(
            t("drive_select_prompt", lang),
            reply_markup=drive_selection(lang, has_personal_drive=has_drive, bot_drive_full=bot_full),
        )

    # ── External URLs (YouTube, Instagram, etc.) ───────────────────────────────

    @app.on_message(filters.private & filters.text & ~filters.command(["start"]))
    async def on_url(client: Client, message: Message):
        user_id = message.from_user.id
        text    = message.text.strip()

        # Skip if the user is in any special input state
        if user_states.get(user_id) in (
            UserState.WAITING_OAUTH_CODE,
            UserState.WAITING_BROADCAST,
            UserState.WAITING_USER_ID,
            UserState.WAITING_CHANNEL_ADD,
            UserState.PENDING_YT_QUALITY,
            UserState.PENDING_DEST_SELECTION,
            UserState.PENDING_DRIVE_SELECTION,
        ):
            return

        if not (text.startswith("http://") or text.startswith("https://")):
            return

        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)

        # ── Google Drive link → checked BEFORE _common_guards ─────────────────
        # (Drive→TG is a download, not an upload — skip force-join / rate limits)
        file_id = extract_gdrive_id(text)
        if file_id:
            try:
                async with AsyncSessionLocal() as session:
                    user2  = await get_or_create_user(session, message.from_user)
                    exempt = await is_upload_exempt(user2)
                if not exempt:
                    await message.reply(
                        t("premium_required_drive", lang),
                        reply_markup=referral_menu(lang),
                    )
                    return
                await _do_gdrive_to_tg(client, message, file_id, user_id, lang)
            except Exception as exc:
                logger.exception("Drive→TG outer error for user %s: %s", user_id, exc)
                try:
                    await message.reply(
                        t("drive_to_tg_error", lang).format(error=str(exc)[:200]),
                        reply_markup=back_to_main(lang),
                    )
                except Exception:
                    pass
            return

        if await _common_guards(client, message, user_id, lang):
            return

        # ── Platform detection ────────────────────────────────────────────────
        platform = detect_source(text)
        if not platform:
            await message.reply(t("url_unsupported", lang))
            return

        # ── YouTube → quality picker first, then destination ─────────────────
        if platform == "YouTube":
            async with AsyncSessionLocal() as session:
                user_yt = await get_or_create_user(session, message.from_user)
                exempt  = await is_upload_exempt(user_yt)

            if not exempt:
                secs = _check_cooldown(user_id)
                if secs:
                    await message.reply(t("upload_cooldown", lang).format(seconds=secs))
                    return

            pending_uploads[user_id] = {
                "type": "url_dest",
                "url":  text,
                "platform": "YouTube",
                "quality_key": None,   # set after quality picker
                "orig": message,
            }
            user_states[user_id] = UserState.PENDING_YT_QUALITY
            await message.reply(t("yt_quality_prompt", lang), reply_markup=yt_quality_menu(lang))
            return

        # ── All other platforms + direct links → destination picker ───────────
        async with AsyncSessionLocal() as session:
            user   = await get_or_create_user(session, message.from_user)
            exempt = await is_upload_exempt(user)

        if not exempt:
            secs = _check_cooldown(user_id)
            if secs:
                await message.reply(t("upload_cooldown", lang).format(seconds=secs))
                return

        icon = source_icon(platform)
        pending_uploads[user_id] = {
            "type": "url_dest",
            "url":  text,
            "platform": platform,
            "quality_key": "best",
            "orig": message,
        }
        user_states[user_id] = UserState.PENDING_DEST_SELECTION
        await message.reply(
            t("dest_select_prompt", lang).format(icon=icon, platform=platform),
            reply_markup=dest_selection(lang),
        )

    # ── Drive selection callbacks ──────────────────────────────────────────────

    @app.on_callback_query(filters.regex("^upload_to_personal$"))
    async def cb_upload_personal(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        async with AsyncSessionLocal() as session:
            lang      = await get_user_lang(session, user_id)
            user      = await get_or_create_user(session, query.from_user)
            has_drive = user.has_personal_drive

        if not has_drive:
            await query.message.edit_text(
                t("auth_required", lang), reply_markup=authenticate_button(lang)
            )
            pending_uploads.pop(user_id, None)
            user_states.pop(user_id, None)
            return

        pending = pending_uploads.pop(user_id, None)
        user_states.pop(user_id, None)
        await query.message.delete()

        if not pending:
            await query.answer("Session expired — please resend the file.", show_alert=True)
            return

        if isinstance(pending, dict) and pending.get("type") == "url":
            orig = pending.get("orig", query.message)
            await _start_url_upload(
                client, orig, pending["path"], pending["name"], pending["size"],
                user_id, lang, use_bot_drive=False,
            )
        else:
            await _start_upload(client, pending, user_id, lang, use_bot_drive=False)

    @app.on_callback_query(filters.regex("^upload_to_bot$"))
    async def cb_upload_bot(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)

        pending = pending_uploads.pop(user_id, None)
        user_states.pop(user_id, None)
        await query.message.delete()

        if not pending:
            await query.answer("Session expired — please resend the file.", show_alert=True)
            return

        if isinstance(pending, dict) and pending.get("type") == "url":
            file_size = pending["size"]
            bot_used  = await _get_bot_drive_used()
            if file_size + bot_used > BOT_DRIVE_MAX_BYTES:
                os.unlink(pending["path"])
                await query.message.reply(t("bot_drive_full", lang), reply_markup=authenticate_button(lang))
                return
            orig = pending.get("orig", query.message)
            await _start_url_upload(
                client, orig, pending["path"], pending["name"], file_size,
                user_id, lang, use_bot_drive=True,
            )
        else:
            orig_message = pending
            file_size    = get_file_size(orig_message) or 0
            bot_used     = await _get_bot_drive_used()
            if file_size + bot_used > BOT_DRIVE_MAX_BYTES:
                await orig_message.reply(t("bot_drive_full", lang), reply_markup=authenticate_button(lang))
                return
            await _start_upload(client, orig_message, user_id, lang, use_bot_drive=True)

    @app.on_callback_query(filters.regex("^bot_drive_full_info$"))
    async def cb_bot_drive_full_info(client: Client, query: CallbackQuery):
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, query.from_user.id)
        await query.answer(t("bot_drive_full", lang)[:200], show_alert=True)

    @app.on_callback_query(filters.regex("^cancel_upload$"))
    async def cb_cancel_upload(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        pending = pending_uploads.pop(user_id, None)
        user_states.pop(user_id, None)
        # Clean up temp file if it was a URL download
        if isinstance(pending, dict) and pending.get("path"):
            try:
                os.unlink(pending["path"])
            except Exception:
                pass
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)
        await query.message.edit_text(t("upload_cancelled", lang), reply_markup=back_to_main(lang))

    # ── YouTube quality selection callbacks ────────────────────────────────────

    @app.on_callback_query(filters.regex(r"^ytq_(best|720|480|audio)$"))
    async def cb_yt_quality(client: Client, query: CallbackQuery):
        user_id     = query.from_user.id
        quality_key = query.matches[0].group(1)

        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)

        pending = pending_uploads.get(user_id)
        if not pending or pending.get("type") != "url_dest":
            await query.answer("Session expired — please resend the link.", show_alert=True)
            return

        # Attach chosen quality; advance to destination selection
        pending["quality_key"] = quality_key
        pending_uploads[user_id] = pending
        user_states[user_id] = UserState.PENDING_DEST_SELECTION

        await query.message.edit_text(
            t("dest_select_prompt", lang).format(icon="🎬", platform="YouTube"),
            reply_markup=dest_selection(lang),
        )

    # ── Destination: Upload to Google Drive ───────────────────────────────────

    @app.on_callback_query(filters.regex("^dest_drive$"))
    async def cb_dest_drive(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)

        pending = pending_uploads.pop(user_id, None)
        user_states.pop(user_id, None)

        if not pending or pending.get("type") != "url_dest":
            await query.answer("Session expired — please resend the link.", show_alert=True)
            return

        url         = pending["url"]
        quality_key = pending.get("quality_key") or "best"
        orig_msg    = pending.get("orig", query.message)

        await query.message.delete()
        await _start_cobalt_upload(client, orig_msg, url, quality_key, user_id, lang)

    # ── Destination: Send to Telegram (auto-delete 2 min) ─────────────────────

    @app.on_callback_query(filters.regex("^dest_telegram$"))
    async def cb_dest_telegram(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)

        pending = pending_uploads.pop(user_id, None)
        user_states.pop(user_id, None)

        if not pending or pending.get("type") != "url_dest":
            await query.answer("Session expired — please resend the link.", show_alert=True)
            return

        url         = pending["url"]
        quality_key = pending.get("quality_key") or "best"
        platform    = pending.get("platform", "Unknown")
        orig_msg    = pending.get("orig", query.message)

        await query.message.delete()
        await _start_tg_delivery(client, orig_msg, url, quality_key, platform, user_id, lang)

    # ── Drive → Telegram button (informational — actual handling is in on_url) ──

    @app.on_callback_query(filters.regex("^drive_to_tg$"))
    async def cb_drive_to_tg(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        async with AsyncSessionLocal() as session:
            lang   = await get_user_lang(session, user_id)
            user   = await get_or_create_user(session, query.from_user)
            exempt = await is_upload_exempt(user)

        if not exempt:
            await query.message.edit_text(
                t("premium_required_drive", lang),
                reply_markup=referral_menu(lang),
            )
            return

        # Just show the prompt — user sends the Drive URL directly in chat
        await query.message.edit_text(
            t("drive_to_tg_prompt", lang),
            reply_markup=back_to_main(lang),
        )


    # ── Catch-all: unsupported content ────────────────────────────────────────

    _SUPPORTED_MEDIA = frozenset((
        "document", "video", "audio", "animation",
        "photo", "voice", "video_note",
    ))

    @app.on_message(filters.private & ~filters.command(["start", "admin"]), group=1)
    async def on_unsupported(client: Client, message: Message):
        user_id = message.from_user.id

        # Skip admin — they may send text in various states
        if user_id == ADMIN_ID:
            return

        # Skip if user is in any state that expects text input
        if user_states.get(user_id) in (
            UserState.WAITING_OAUTH_CODE,
            UserState.PENDING_DRIVE_SELECTION,
        ):
            return

        # Skip supported media types (handled by on_file)
        if any(getattr(message, attr, None) for attr in _SUPPORTED_MEDIA):
            return

        # Skip URLs (handled by on_url / on_drive_link)
        if message.text and (
            message.text.strip().startswith("http://")
            or message.text.strip().startswith("https://")
        ):
            return

        # Everything else: stickers, polls, locations, plain text, forwards, etc.
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)
        await message.reply(t("unsupported_message", lang))


# ── Core upload logic ─────────────────────────────────────────────────────────

async def _do_drive_upload(
    user_id: int,
    lang: str,
    file_path: str,
    file_name: str,
    file_size: int,
    status_msg,
    use_bot_drive: bool,
) -> None:
    """Upload *file_path* to Drive and edit *status_msg* with results."""
    if use_bot_drive:
        loop    = asyncio.get_event_loop()
        service = await loop.run_in_executor(None, build_bot_service)
        new_token   = None
        folder_id   = BOT_DRIVE_FOLDER_ID
    else:
        async with AsyncSessionLocal() as session:
            user = await session.get(UserModel, user_id)
        service, new_token = build_user_service(user.oauth_access_token, user.oauth_refresh_token)
        folder_id = ""
        if new_token != user.oauth_access_token:
            async with AsyncSessionLocal() as session:
                u = await session.get(UserModel, user_id)
                if u:
                    u.oauth_access_token = new_token
                    await session.commit()

    up_bar = ProgressBar(file_size)
    loop   = asyncio.get_event_loop()
    header = t("upload_header_bot" if use_bot_drive else "upload_header", lang)

    async def on_up(current: int, total: int) -> None:
        if up_bar.should_update():
            try:
                await status_msg.edit_text(up_bar.render(current, header))
            except Exception:
                pass

    file_id, share_link = await loop.run_in_executor(
        None, sync_upload, file_path, file_name, service, on_up, loop, folder_id
    )

    async with AsyncSessionLocal() as session:
        session.add(Upload(
            user_id=user_id,
            service_account_id=None,
            gdrive_file_id=file_id,
            file_name=file_name,
            file_size_bytes=file_size,
            share_link=share_link,
            is_personal_drive=not use_bot_drive,
        ))
        await session.commit()

    async with AsyncSessionLocal() as session:
        await increment_daily_usage(session, user_id, file_size)

    await status_msg.edit_text(
        t("upload_complete", lang).format(
            name=file_name,
            size=format_bytes(file_size),
            link=share_link,
        ),
        disable_web_page_preview=True,
    )


async def _start_upload(
    client: Client,
    message: Message,
    user_id: int,
    lang: str,
    use_bot_drive: bool,
) -> None:
    """Download from Telegram then upload to Drive."""
    currently_uploading.add(user_id)
    await update_rate_limit(user_id)

    file_name  = get_file_name(message)
    file_size  = get_file_size(message) or 0
    status_msg = await message.reply(t("upload_starting", lang))
    temp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, dir="temp", suffix=f"_{file_name}") as tmp:
            temp_path = tmp.name

        dl_bar = ProgressBar(file_size)

        async def on_dl(current: int, total: int) -> None:
            if dl_bar.should_update():
                try:
                    await status_msg.edit_text(dl_bar.render(current, t("download_header", lang)))
                except Exception:
                    pass

        await message.download(file_name=temp_path, progress=on_dl)
        actual_size = os.path.getsize(temp_path)

        await _do_drive_upload(user_id, lang, temp_path, file_name, actual_size, status_msg, use_bot_drive)

    except Exception:
        logger.exception("Upload failed for user %s (bot_drive=%s)", user_id, use_bot_drive)
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


async def _do_gdrive_to_tg(
    client: Client,
    message: Message,
    file_id: str,
    user_id: int,
    lang: str,
) -> None:
    """Download a public Google Drive file and send it back as a Telegram document."""
    logger.info("Drive→TG start: user=%s file_id=%s", user_id, file_id)
    try:
        status_msg = await message.reply(t("drive_to_tg_downloading", lang))
    except Exception as exc:
        logger.error("Drive→TG: failed to send status msg: %s", exc)
        return
    temp_path: str | None = None
    try:
        temp_path, filename = await download_gdrive(file_id, "temp")
    except Exception as exc:
        logger.warning("GDrive download failed user=%s id=%s: %s", user_id, file_id, exc)
        await status_msg.edit_text(
            t("drive_to_tg_error", lang).format(error=str(exc)[:300]),
            reply_markup=back_to_main(lang),
        )
        return

    if not temp_path or not os.path.exists(temp_path):
        await status_msg.edit_text(
            t("drive_to_tg_not_public", lang),
            reply_markup=back_to_main(lang),
        )
        return

    file_size = os.path.getsize(temp_path)
    if file_size > MAX_FILE_SIZE_BYTES:
        os.unlink(temp_path)
        await status_msg.edit_text(
            t("upload_too_large", lang).format(size=format_bytes(file_size)),
            reply_markup=back_to_main(lang),
        )
        return

    try:
        await status_msg.edit_text(t("drive_to_tg_sending", lang))
        await client.send_document(
            chat_id=user_id,
            document=temp_path,
            file_name=filename,
            caption=f"📎 `{filename}`\n💾 {format_bytes(file_size)}",
        )
        await status_msg.delete()
    except Exception as exc:
        logger.exception("Failed to send GDrive file to user %s", user_id)
        try:
            await status_msg.edit_text(
                t("drive_to_tg_error", lang).format(error=str(exc)[:200]),
                reply_markup=back_to_main(lang),
            )
        except Exception:
            pass
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass


async def _start_url_upload(
    client: Client,
    message: Message,
    file_path: str,
    file_name: str,
    file_size: int,
    user_id: int,
    lang: str,
    use_bot_drive: bool,
) -> None:
    """Upload a pre-downloaded file (from yt-dlp) to Drive."""
    currently_uploading.add(user_id)
    await update_rate_limit(user_id)

    status_msg = await message.reply(t("upload_starting", lang))
    try:
        await _do_drive_upload(user_id, lang, file_path, file_name, file_size, status_msg, use_bot_drive)
    except Exception:
        logger.exception("URL upload failed for user %s", user_id)
        try:
            await status_msg.edit_text(t("upload_failed", lang))
        except Exception:
            pass
    finally:
        currently_uploading.discard(user_id)
        if os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except Exception:
                pass


async def _start_cobalt_upload(
    client: Client,
    message: Message,
    url: str,
    quality_key: str,
    user_id: int,
    lang: str,
) -> None:
    """Download YouTube URL (yt-dlp primary, cobalt.tools fallback) then upload to Drive."""
    icon = "🎵" if quality_key == "audio" else "🎬"
    status_msg = await message.reply(
        t("download_header_url", lang).format(icon=icon, platform="YouTube")
    )
    temp_path: str | None = None

    try:
        # Primary: yt-dlp with the chosen quality
        dl_bar = ProgressBar(0)

        async def on_dl(current: int, total: int) -> None:
            dl_bar.total = total
            if dl_bar.should_update():
                try:
                    await status_msg.edit_text(
                        dl_bar.render(current, t("download_header_url", lang).format(
                            icon=icon, platform="YouTube"
                        ))
                    )
                except Exception:
                    pass

        try:
            temp_path, title = await download_url(url, "temp", quality_key, on_dl)
        except Exception as ytdlp_exc:
            logger.warning("yt-dlp failed for YT (quality=%s), trying cobalt: %s", quality_key, ytdlp_exc)
            # Fallback: cobalt.tools
            try:
                temp_path, title = await download_via_cobalt(url, "temp", quality_key)
            except Exception as cobalt_exc:
                logger.warning("cobalt also failed for user=%s: %s", user_id, cobalt_exc)
                err = str(cobalt_exc)[:300]
                try:
                    await status_msg.edit_text(t("url_download_failed", lang) + f"\n\n`{err}`")
                except Exception:
                    pass
                return

        if not temp_path or not os.path.exists(temp_path):
            await status_msg.edit_text(t("url_download_failed", lang))
            return

        file_size = os.path.getsize(temp_path)
        if file_size > MAX_FILE_SIZE_BYTES:
            os.unlink(temp_path)
            await status_msg.edit_text(t("upload_too_large", lang).format(size=format_bytes(file_size)))
            return

        async with AsyncSessionLocal() as session:
            user_obj = await get_or_create_user(session, message.from_user)
            has_drive = user_obj.has_personal_drive
            daily_limited, reason = await check_daily_limit(session, user_obj, file_size)

        if daily_limited:
            os.unlink(temp_path)
            key = "daily_limit_count" if reason == "count" else "daily_limit_size"
            await status_msg.edit_text(t(key, lang), reply_markup=referral_menu(lang))
            return

        safe_title = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', title)[:100].strip()
        ext = os.path.splitext(temp_path)[1] or (".mp3" if quality_key == "audio" else ".mp4")
        file_name = safe_title + ext

        upload_cooldowns[user_id] = time.time()

        if not BOT_DRIVE_SA_JSON:
            # Only personal drive available
            if not has_drive:
                os.unlink(temp_path)
                await status_msg.edit_text(t("auth_required", lang), reply_markup=authenticate_button(lang))
                return
            await status_msg.delete()
            await _start_url_upload(client, message, temp_path, file_name, file_size, user_id, lang, use_bot_drive=False)
            return

        # Bot drive configured — show drive selection
        bot_used = await _get_bot_drive_used()
        bot_full = file_size + bot_used > BOT_DRIVE_MAX_BYTES
        pending_uploads[user_id] = {
            "type": "url",
            "path": temp_path,
            "name": file_name,
            "size": file_size,
            "orig": message,
        }
        user_states[user_id] = UserState.PENDING_DRIVE_SELECTION
        await status_msg.edit_text(
            t("drive_select_prompt", lang),
            reply_markup=drive_selection(lang, has_personal_drive=has_drive, bot_drive_full=bot_full),
        )
        # temp_path cleaned up by drive selection callback or cancel handler

    except Exception:
        logger.exception("YT upload failed for user %s", user_id)
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass
        try:
            await status_msg.edit_text(t("upload_failed", lang))
        except Exception:
            pass


# ── Telegram-delivery helpers ─────────────────────────────────────────────────

async def _schedule_delete(
    client,
    chat_id: int,
    *message_ids: int,
    delay: int = 120,
) -> None:
    """Delete *message_ids* from *chat_id* after *delay* seconds."""
    await asyncio.sleep(delay)
    for mid in message_ids:
        try:
            await client.delete_messages(chat_id, mid)
        except Exception:
            pass


async def _start_tg_delivery(
    client,
    message,
    url: str,
    quality_key: str,
    platform: str,
    user_id: int,
    lang: str,
) -> None:
    """
    Download URL and send the file directly to the user's Telegram chat.
    The file and warning message are auto-deleted after 2 minutes.
    Server temp file is always deleted immediately after sending.
    """
    icon = source_icon(platform)
    status_msg = await message.reply(
        t("download_header_url", lang).format(icon=icon, platform=platform)
    )
    temp_path: str | None = None

    try:
        dl_bar = ProgressBar(0)

        async def on_dl(current: int, total: int) -> None:
            dl_bar.total = total
            if dl_bar.should_update():
                try:
                    await status_msg.edit_text(
                        dl_bar.render(
                            current,
                            t("download_header_url", lang).format(icon=icon, platform=platform),
                        )
                    )
                except Exception:
                    pass

        # Three-layer fallback: yt-dlp → cobalt → direct HTTP
        try:
            temp_path, title = await download_url(url, "temp", quality_key, on_dl)
        except Exception as e1:
            logger.warning("yt-dlp failed TG delivery (platform=%s): %s", platform, e1)
            try:
                temp_path, title = await download_via_cobalt(url, "temp", quality_key)
            except Exception as e2:
                logger.warning("cobalt failed TG delivery: %s", e2)
                try:
                    temp_path, title = await download_direct(url, "temp")
                except Exception as e3:
                    err = str(e3)[:300]
                    await status_msg.edit_text(t("url_download_failed", lang) + f"\n\n`{err}`")
                    return

        if not temp_path or not os.path.exists(temp_path):
            await status_msg.edit_text(t("url_download_failed", lang))
            return

        file_size = os.path.getsize(temp_path)
        if file_size > MAX_FILE_SIZE_BYTES:
            os.unlink(temp_path)
            await status_msg.edit_text(
                t("upload_too_large", lang).format(size=format_bytes(file_size))
            )
            return

        safe_title = re.sub(r'[<>:"/\\|?*\n\r\t]', "_", title)[:100].strip()
        ext = os.path.splitext(temp_path)[1] or (".mp3" if quality_key == "audio" else ".mp4")
        file_name = safe_title + ext

        await status_msg.edit_text(t("tg_sending", lang))

        sent_msg = await client.send_document(
            chat_id=user_id,
            document=temp_path,
            file_name=file_name,
            caption=t("tg_delivery_caption", lang).format(
                name=file_name,
                size=format_bytes(file_size),
            ),
        )

        warn_msg = await client.send_message(
            chat_id=user_id,
            text=t("tg_delivery_warning", lang),
        )

        await status_msg.delete()

        # Fire-and-forget: auto-delete both messages after 2 minutes
        asyncio.create_task(
            _schedule_delete(client, user_id, sent_msg.id, warn_msg.id, delay=120)
        )

    except Exception:
        logger.exception("TG delivery failed for user %s", user_id)
        try:
            await status_msg.edit_text(t("url_download_failed", lang))
        except Exception:
            pass
    finally:
        # Always wipe temp file immediately — server disk is not persistent storage
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass
