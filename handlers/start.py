import json
import logging

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message
from sqlalchemy import func, select

from config import ADMIN_ID, REFERRAL_UNLOCK_COUNT
from database.models import Upload, User
from database.session import AsyncSessionLocal
from services.force_join import get_force_join_channels, get_unjoined_channels
from utils.helpers import get_or_create_user, get_referral_count, get_setting, get_user_lang
from utils.keyboards import back_to_main, force_join, language_selection, main_menu, referral_menu, reply_main_menu
from utils.progress import format_bytes
from utils.strings import t

logger = logging.getLogger(__name__)


def register(app: Client) -> None:

    @app.on_message(filters.command("start") & filters.private)
    async def cmd_start(client: Client, message: Message):
        async with AsyncSessionLocal() as session:
            bot_status = await get_setting(session, "bot_status", "on")

        if bot_status == "off" and message.from_user.id != ADMIN_ID:
            await message.reply(
                "🔴 Bot is under maintenance. / ربات در حال تعمیر است.\n\n"
                "Please try again later. / لطفاً بعداً تلاش کنید."
            )
            return

        args = message.text.split(maxsplit=1)
        ref_code = args[1].strip() if len(args) > 1 else ""

        # ── Auto-message deep link ─────────────────────────────────────────
        if ref_code == "autostart":
            async with AsyncSessionLocal() as session:
                user     = await get_or_create_user(session, message.from_user)
                auto_raw = await get_setting(session, "auto_message", "")
                lang     = user.language or "en"
            if auto_raw:
                try:
                    await _send_auto_message(client, message.from_user.id, auto_raw)
                except Exception:
                    logger.exception("Failed to send auto-message to %s", message.from_user.id)
            await _show_main_or_join(client, message, lang, message.from_user.id)
            return

        async with AsyncSessionLocal() as session:
            is_new = await session.get(User, message.from_user.id) is None
            user = await get_or_create_user(session, message.from_user)

            if is_new and ref_code.startswith("ref_"):
                try:
                    referrer_id = int(ref_code[4:])
                    if referrer_id != message.from_user.id:
                        user.referred_by_id = referrer_id
                        await session.commit()
                        await session.refresh(user)
                        await _maybe_unlock_referrer(session, referrer_id)
                except (ValueError, Exception):
                    pass

            lang = user.language

        if lang not in ("en", "fa"):
            if is_new and ref_code.startswith("ref_"):
                await message.reply(t("referral_welcome", "en"))
            await message.reply(
                t("choose_language", "en"),
                reply_markup=language_selection(),
            )
            return

        await _show_main_or_join(client, message, lang, message.from_user.id)

    @app.on_callback_query(filters.regex(r"^set_lang_(en|fa)$"))
    async def cb_set_language(client: Client, query: CallbackQuery):
        lang = query.matches[0].group(1)
        user_id = query.from_user.id

        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(session, query.from_user)
            user.language = lang
            await session.commit()

        async with AsyncSessionLocal() as session:
            bot_status = await get_setting(session, "bot_status", "on")

        if bot_status == "off" and user_id != ADMIN_ID:
            await query.message.edit_text(t("bot_offline", lang))
            return

        await _show_main_or_join_query(client, query, lang, user_id)

    @app.on_callback_query(filters.regex("^check_join$"))
    async def cb_check_join(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)

        unjoined = await get_unjoined_channels(client, user_id)
        if unjoined:
            await query.answer(
                "You still haven't joined all channels! / هنوز در همه کانال‌ها عضو نشدید!",
                show_alert=True,
            )
            return

        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(session, query.from_user)
            is_admin = user_id == ADMIN_ID or bool(user.is_admin)
        await query.message.edit_text(
            await _build_welcome(lang),
            reply_markup=main_menu(lang=lang, is_admin=is_admin,
                                   has_personal_drive=user.has_personal_drive),
        )

    @app.on_callback_query(filters.regex("^main_menu$"))
    async def cb_main_menu(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(session, query.from_user)
            lang = user.language or "en"
            is_admin = user_id == ADMIN_ID or bool(user.is_admin)
        await query.message.edit_text(
            await _build_welcome(lang),
            reply_markup=main_menu(lang=lang, is_admin=is_admin,
                                   has_personal_drive=user.has_personal_drive),
        )

    @app.on_callback_query(filters.regex("^upload_info$"))
    async def cb_upload_info(client: Client, query: CallbackQuery):
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, query.from_user.id)
        await query.answer(t("upload_hint", lang), show_alert=True)

    @app.on_callback_query(filters.regex("^my_stats$"))
    async def cb_my_stats(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)

            total = (
                await session.execute(select(func.count()).where(Upload.user_id == user_id))
            ).scalar() or 0

            size_sum = (
                await session.execute(
                    select(func.sum(Upload.file_size_bytes)).where(
                        Upload.user_id == user_id, Upload.is_deleted.is_(False)
                    )
                )
            ).scalar() or 0

        text = t("my_stats", lang).format(total=f"{total:,}", size=format_bytes(size_sum))
        await query.message.edit_text(text, reply_markup=back_to_main(lang))

    @app.on_callback_query(filters.regex("^referral$"))
    async def cb_referral(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)
            count = await get_referral_count(session, user_id)
            user = await session.get(User, user_id)
            unlocked = bool(user.referral_unlocked) if user else False

        from utils import bot_info
        link = f"https://t.me/{bot_info.BOT_USERNAME}?start=ref_{user_id}"
        status = t("referral_unlocked_badge", lang) if unlocked else t("referral_pending_badge", lang)
        text = t("referral_info", lang).format(
            link=link,
            count=count,
            needed=REFERRAL_UNLOCK_COUNT,
            status=status,
        )
        await query.message.edit_text(text, reply_markup=referral_menu(lang))

    # ── Reply keyboard button handlers ────────────────────────────────────────

    @app.on_message(filters.private & filters.text)
    async def on_reply_kb_button(client: Client, message: Message):
        """Route presses on the persistent reply keyboard to the correct action."""
        text = message.text.strip()
        user_id = message.from_user.id

        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)

        # Map button texts in both languages to actions
        upload_labels   = {t("rbtn_upload",   "en"), t("rbtn_upload",   "fa")}
        drive_labels    = {t("rbtn_my_drive", "en"), t("rbtn_my_drive", "fa")}
        stats_labels    = {t("rbtn_stats",    "en"), t("rbtn_stats",    "fa")}
        referral_labels = {t("rbtn_referral", "en"), t("rbtn_referral", "fa")}

        if text in upload_labels:
            await message.reply(t("upload_hint", lang))
        elif text in drive_labels:
            async with AsyncSessionLocal() as session:
                user = await get_or_create_user(session, message.from_user)
                has_drive = user.has_personal_drive
            from utils.keyboards import authenticate_button, drive_status_menu
            if has_drive:
                await message.reply(t("drive_status_text", lang), reply_markup=drive_status_menu(lang))
            else:
                await message.reply(t("auth_required", lang), reply_markup=authenticate_button(lang))
        elif text in stats_labels:
            async with AsyncSessionLocal() as session:
                total = (
                    await session.execute(select(func.count()).where(Upload.user_id == user_id))
                ).scalar() or 0
                size_sum = (
                    await session.execute(
                        select(func.sum(Upload.file_size_bytes)).where(
                            Upload.user_id == user_id, Upload.is_deleted.is_(False)
                        )
                    )
                ).scalar() or 0
            await message.reply(
                t("my_stats", lang).format(total=f"{total:,}", size=format_bytes(size_sum)),
                reply_markup=back_to_main(lang),
            )
        elif text in referral_labels:
            async with AsyncSessionLocal() as session:
                count = await get_referral_count(session, user_id)
                user  = await session.get(User, user_id)
                unlocked = bool(user.referral_unlocked) if user else False
            from utils import bot_info
            link   = f"https://t.me/{bot_info.BOT_USERNAME}?start=ref_{user_id}"
            status = t("referral_unlocked_badge", lang) if unlocked else t("referral_pending_badge", lang)
            await message.reply(
                t("referral_info", lang).format(
                    link=link, count=count, needed=REFERRAL_UNLOCK_COUNT, status=status
                ),
                reply_markup=referral_menu(lang),
            )

    # support button removed — channels shown in welcome text instead


async def _maybe_unlock_referrer(session, referrer_id: int) -> None:
    referrer = await session.get(User, referrer_id)
    if not referrer or referrer.referral_unlocked:
        return
    count = await get_referral_count(session, referrer_id)
    if count >= REFERRAL_UNLOCK_COUNT:
        referrer.referral_unlocked = True
        await session.commit()


async def _build_welcome(lang: str) -> str:
    """Build welcome text with channel list appended."""
    async with AsyncSessionLocal() as session:
        channels = await get_force_join_channels(session)
    text = t("welcome", lang)
    if channels:
        ch_str = " · ".join(channels)
        text += f"\n\n{t('channels_footer', lang).format(channels=ch_str)}"
    return text


async def _show_main_or_join(client: Client, message: Message, lang: str, user_id: int):
    unjoined = await get_unjoined_channels(client, user_id)
    if unjoined:
        await message.reply(
            t("force_join_prompt", lang),
            reply_markup=force_join(unjoined, lang),
        )
        return

    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        is_admin = user_id == ADMIN_ID or (bool(user.is_admin) if user else False)
        has_drive = user.has_personal_drive if user else False

    # Send reply keyboard first so it appears at the bottom
    await message.reply(t("reply_kb_hint", lang), reply_markup=reply_main_menu(lang))
    await message.reply(
        await _build_welcome(lang),
        reply_markup=main_menu(lang=lang, is_admin=is_admin, has_personal_drive=has_drive),
    )


async def _show_main_or_join_query(client: Client, query: CallbackQuery, lang: str, user_id: int):
    unjoined = await get_unjoined_channels(client, user_id)
    if unjoined:
        await query.message.edit_text(
            t("force_join_prompt", lang),
            reply_markup=force_join(unjoined, lang),
        )
        return

    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        is_admin = user_id == ADMIN_ID or (bool(user.is_admin) if user else False)
        has_drive = user.has_personal_drive if user else False

    # Send reply keyboard as a separate message (can't combine with edit_text)
    await query.message.reply(t("reply_kb_hint", lang), reply_markup=reply_main_menu(lang))
    await query.message.edit_text(
        await _build_welcome(lang),
        reply_markup=main_menu(lang=lang, is_admin=is_admin, has_personal_drive=has_drive),
    )


async def _send_auto_message(client: Client, user_id: int, raw: str) -> None:
    """Send the stored auto-message to user_id."""
    payload = json.loads(raw)
    msg_type = payload.get("type")
    file_id  = payload.get("file_id", "")
    caption  = payload.get("caption") or None
    text     = payload.get("text", "")

    if msg_type == "text":
        await client.send_message(user_id, text)
    elif msg_type == "photo":
        await client.send_photo(user_id, file_id, caption=caption)
    elif msg_type == "video":
        await client.send_video(user_id, file_id, caption=caption)
    elif msg_type == "document":
        await client.send_document(user_id, file_id, caption=caption)
    elif msg_type == "audio":
        await client.send_audio(user_id, file_id, caption=caption)
    elif msg_type == "voice":
        await client.send_voice(user_id, file_id, caption=caption)
    elif msg_type == "animation":
        await client.send_animation(user_id, file_id, caption=caption)
    elif msg_type == "video_note":
        await client.send_video_note(user_id, file_id)
    elif msg_type == "sticker":
        await client.send_sticker(user_id, file_id)
