import asyncio
import logging

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message
from sqlalchemy import func, select

from config import ADMIN_ID
from database.models import Upload, User
from database.session import AsyncSessionLocal
from services.force_join import get_force_join_channels
from utils.helpers import (
    get_referral_count,
    get_setting,
    get_user_lang,
    set_setting,
)
import json

from utils.keyboards import (
    _PAGE_SIZE,
    admin_auto_msg_menu,
    admin_channels_menu,
    admin_panel,
    admin_user_actions,
    admin_users_list,
    back_to_main,
    cancel_action,
    main_menu,
)
from utils.progress import format_bytes
from utils import bot_info
from utils.state import UserState, user_state_data, user_states
from utils.strings import t

logger = logging.getLogger(__name__)

_ADMIN_CB  = filters.user(ADMIN_ID)
_ADMIN_MSG = filters.user(ADMIN_ID) & filters.private


def register(app: Client) -> None:

    @app.on_message(_ADMIN_MSG & filters.command("admin"))
    async def cmd_admin(client: Client, message: Message):
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)
            status = await get_setting(session, "bot_status", "on")
        await message.reply(
            t("admin_panel_title", lang),
            reply_markup=admin_panel(lang=lang, bot_on=(status == "on")),
        )

    @app.on_callback_query(_ADMIN_CB & filters.regex("^admin_panel$"))
    async def cb_admin_panel(client: Client, query: CallbackQuery):
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)
            status = await get_setting(session, "bot_status", "on")
        await query.message.edit_text(
            t("admin_panel_title", lang),
            reply_markup=admin_panel(lang=lang, bot_on=(status == "on")),
        )

    @app.on_callback_query(_ADMIN_CB & filters.regex("^admin_stats$"))
    async def cb_admin_stats(client: Client, query: CallbackQuery):
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)

            users_total = (
                await session.execute(select(func.count(User.id)))
            ).scalar() or 0

            uploads_total = (
                await session.execute(select(func.count(Upload.id)))
            ).scalar() or 0

            stored_bytes = (
                await session.execute(
                    select(func.sum(Upload.file_size_bytes))
                    .where(Upload.is_deleted.is_(False))
                )
            ).scalar() or 0

        text = t("admin_stats", lang).format(
            users=f"{users_total:,}",
            uploads=f"{uploads_total:,}",
            size=format_bytes(stored_bytes),
        )
        await query.message.edit_text(text, reply_markup=back_to_main(lang))

    @app.on_callback_query(_ADMIN_CB & filters.regex("^admin_broadcast$"))
    async def cb_broadcast_prompt(client: Client, query: CallbackQuery):
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)
        user_states[ADMIN_ID] = UserState.WAITING_BROADCAST
        await query.message.edit_text(
            t("broadcast_prompt", lang),
            reply_markup=cancel_action(lang),
        )

    @app.on_callback_query(_ADMIN_CB & filters.regex(r"^admin_users(?:_page_(\d+))?$"))
    async def cb_admin_users(client: Client, query: CallbackQuery):
        page = int(query.matches[0].group(1) or 0)
        async with AsyncSessionLocal() as session:
            lang  = await get_user_lang(session, ADMIN_ID)
            total = (await session.execute(select(func.count(User.id)))).scalar() or 0
            users = (await session.execute(
                select(User).order_by(User.joined_at.desc())
                .offset(page * _PAGE_SIZE).limit(_PAGE_SIZE)
            )).scalars().all()
        pages = max(1, (total + _PAGE_SIZE - 1) // _PAGE_SIZE)
        text = t("admin_users_header", lang).format(page=page + 1, pages=pages, total=total)
        text += "\n" + "━" * 22 + "\n"
        text += _format_users_table(users, lang)
        await query.message.edit_text(text, reply_markup=admin_users_list(users, page, total, lang))

    @app.on_callback_query(_ADMIN_CB & filters.regex(r"^admin_view_user_(\d+)$"))
    async def cb_view_user(client: Client, query: CallbackQuery):
        target_id = int(query.matches[0].group(1))
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)
        await _show_user_info(query, target_id, lang)

    @app.on_callback_query(_ADMIN_CB & filters.regex("^admin_user_search$"))
    async def cb_admin_user_search(client: Client, query: CallbackQuery):
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)
        user_states[ADMIN_ID] = UserState.WAITING_USER_ID
        await query.message.edit_text(
            t("admin_ask_user_id", lang),
            reply_markup=cancel_action(lang),
        )

    @app.on_callback_query(_ADMIN_CB & filters.regex("^admin_channels$"))
    async def cb_admin_channels(client: Client, query: CallbackQuery):
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)
            channels = await get_force_join_channels(session)
        title = t("channels_menu_title", lang)
        if not channels:
            title += f"\n{t('channels_empty', lang)}"
        await query.message.edit_text(
            title,
            reply_markup=admin_channels_menu(channels, lang),
        )

    @app.on_callback_query(_ADMIN_CB & filters.regex("^admin_add_channel$"))
    async def cb_admin_add_channel(client: Client, query: CallbackQuery):
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)
        user_states[ADMIN_ID] = UserState.WAITING_CHANNEL_ADD
        await query.message.edit_text(
            t("admin_ask_channel", lang),
            reply_markup=cancel_action(lang),
        )

    @app.on_callback_query(_ADMIN_CB & filters.regex(r"^admin_rm_ch_(.+)$"))
    async def cb_admin_rm_channel(client: Client, query: CallbackQuery):
        ch_handle = query.matches[0].group(1)
        channel = f"@{ch_handle}"
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)
            channels = await get_force_join_channels(session)
            if channel in channels:
                channels.remove(channel)
            new_value = ",".join(channels)
            await set_setting(session, "force_join_channels", new_value)
            channels = await get_force_join_channels(session)
        await query.answer(t("admin_channel_removed", lang))
        title = t("channels_menu_title", lang)
        if not channels:
            title += f"\n{t('channels_empty', lang)}"
        await query.message.edit_text(title, reply_markup=admin_channels_menu(channels, lang))

    @app.on_callback_query(_ADMIN_CB & filters.regex(r"^admin_mk_admin_(\d+)$"))
    async def cb_mk_admin(client: Client, query: CallbackQuery):
        target_id = int(query.matches[0].group(1))
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)
            user = await session.get(User, target_id)
            if user:
                user.is_admin = True
                await session.commit()
        await query.answer(t("admin_action_done", lang))
        await _show_user_info(query, target_id, lang)

    @app.on_callback_query(_ADMIN_CB & filters.regex(r"^admin_rm_admin_(\d+)$"))
    async def cb_rm_admin(client: Client, query: CallbackQuery):
        target_id = int(query.matches[0].group(1))
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)
            user = await session.get(User, target_id)
            if user:
                user.is_admin = False
                await session.commit()
        await query.answer(t("admin_action_done", lang))
        await _show_user_info(query, target_id, lang)

    @app.on_callback_query(_ADMIN_CB & filters.regex(r"^admin_grant_exempt_(\d+)$"))
    async def cb_grant_exempt(client: Client, query: CallbackQuery):
        target_id = int(query.matches[0].group(1))
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)
            user = await session.get(User, target_id)
            if user:
                user.upload_limit_exempt = True
                await session.commit()
        await query.answer(t("admin_action_done", lang))
        await _show_user_info(query, target_id, lang)

    @app.on_callback_query(_ADMIN_CB & filters.regex(r"^admin_revoke_exempt_(\d+)$"))
    async def cb_revoke_exempt(client: Client, query: CallbackQuery):
        target_id = int(query.matches[0].group(1))
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)
            user = await session.get(User, target_id)
            if user:
                user.upload_limit_exempt = False
                await session.commit()
        await query.answer(t("admin_action_done", lang))
        await _show_user_info(query, target_id, lang)

    # ── Auto message ──────────────────────────────────────────────────────────

    @app.on_callback_query(_ADMIN_CB & filters.regex("^admin_auto_msg$"))
    async def cb_admin_auto_msg(client: Client, query: CallbackQuery):
        async with AsyncSessionLocal() as session:
            lang     = await get_user_lang(session, ADMIN_ID)
            saved    = await get_setting(session, "auto_message", "")
        has_msg = bool(saved)
        link = f"https://t.me/{bot_info.BOT_USERNAME}?start=autostart"
        if has_msg:
            text = t("admin_auto_msg_status_set", lang).format(link=link)
        else:
            text = t("admin_auto_msg_status_none", lang)
        # Show set/replace prompt inline — admin just sends a message
        user_states[ADMIN_ID] = UserState.WAITING_AUTO_MSG
        await query.message.edit_text(
            t("admin_auto_msg_prompt", lang),
            reply_markup=admin_auto_msg_menu(has_msg, lang),
        )

    @app.on_callback_query(_ADMIN_CB & filters.regex("^admin_auto_msg_clear$"))
    async def cb_auto_msg_clear(client: Client, query: CallbackQuery):
        async with AsyncSessionLocal() as session:
            lang   = await get_user_lang(session, ADMIN_ID)
            await set_setting(session, "auto_message", "")
            status = await get_setting(session, "bot_status", "on")
        user_states.pop(ADMIN_ID, None)
        await query.answer(t("admin_auto_msg_cleared", lang), show_alert=True)
        await query.message.edit_text(
            t("admin_panel_title", lang),
            reply_markup=admin_panel(lang=lang, bot_on=(status == "on")),
        )

    @app.on_message(_ADMIN_MSG & ~filters.command(["start", "admin"]))
    async def handle_admin_input(client: Client, message: Message):
        state = user_states.get(ADMIN_ID)

        if state == UserState.WAITING_BROADCAST:
            await _do_broadcast(client, message)
            return

        if state == UserState.WAITING_USER_ID:
            await _handle_user_lookup(client, message)
            return

        if state == UserState.WAITING_CHANNEL_ADD:
            await _handle_channel_add(client, message)
            return

        if state == UserState.WAITING_AUTO_MSG:
            await _handle_auto_msg_save(client, message)
            return

    async def _do_broadcast(client: Client, broadcast_msg: Message):
        user_states.pop(ADMIN_ID, None)
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)

        status = await broadcast_msg.reply(t("broadcast_sending", lang))

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User.id).where(User.id != ADMIN_ID, User.is_banned.is_(False))
            )
            user_ids = result.scalars().all()

        success, failed = 0, 0
        for uid in user_ids:
            try:
                await broadcast_msg.copy(uid)
                success += 1
                await asyncio.sleep(0.05)
            except Exception:
                failed += 1

        await status.edit_text(
            t("broadcast_done", lang).format(ok=f"{success:,}", fail=f"{failed:,}")
        )

    async def _handle_user_lookup(client: Client, message: Message):
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)

        text = message.text.strip() if message.text else ""
        if not text.isdigit():
            await message.reply(t("admin_ask_user_id", lang))
            return

        user_states.pop(ADMIN_ID, None)
        target_id = int(text)

        async with AsyncSessionLocal() as session:
            user = await session.get(User, target_id)
            if not user:
                await message.reply(t("admin_user_not_found", lang))
                return
            refs = await get_referral_count(session, target_id)
            info = t("admin_user_info", lang).format(
                id=user.id,
                name=user.first_name or "-",
                username=user.username or "-",
                lang=user.language or "-",
                joined=str(user.joined_at)[:10] if user.joined_at else "-",
                drive="✅" if user.has_personal_drive else "❌",
                is_admin="✅" if user.is_admin else "❌",
                exempt="✅" if user.upload_limit_exempt else "❌",
                refs=refs,
                daily_count=user.daily_upload_count or 0,
                daily_size=format_bytes(user.daily_upload_bytes or 0),
            )

        await message.reply(
            info,
            reply_markup=admin_user_actions(
                target_id, lang,
                is_admin_flag=bool(user.is_admin),
                is_exempt=bool(user.upload_limit_exempt),
            ),
        )

    async def _handle_channel_add(client: Client, message: Message):
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)

        text = message.text.strip() if message.text else ""
        if not text.startswith("@") or len(text) < 2:
            await message.reply(t("admin_channel_invalid", lang))
            return

        user_states.pop(ADMIN_ID, None)
        channel = text if text.startswith("@") else f"@{text}"

        async with AsyncSessionLocal() as session:
            channels = await get_force_join_channels(session)
            if channel not in channels:
                channels.append(channel)
            await set_setting(session, "force_join_channels", ",".join(channels))
            channels = await get_force_join_channels(session)

        await message.reply(
            t("admin_channel_added", lang),
            reply_markup=admin_channels_menu(channels, lang),
        )

    @app.on_callback_query(_ADMIN_CB & filters.regex("^admin_bot_(on|off)$"))
    async def cb_bot_toggle(client: Client, query: CallbackQuery):
        new_state = query.matches[0].group(1)
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)
            await set_setting(session, "bot_status", new_state)

        key = "bot_toggled_on" if new_state == "on" else "bot_toggled_off"
        await query.answer(t(key, lang), show_alert=True)
        await query.message.edit_text(
            t("admin_panel_title", lang),
            reply_markup=admin_panel(lang=lang, bot_on=(new_state == "on")),
        )

    @app.on_callback_query(_ADMIN_CB & filters.regex("^cancel_action$"))
    async def cb_cancel_admin(client: Client, query: CallbackQuery):
        user_states.pop(ADMIN_ID, None)
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)
            status = await get_setting(session, "bot_status", "on")
        await query.message.edit_text(
            t("admin_panel_title", lang),
            reply_markup=admin_panel(lang=lang, bot_on=(status == "on")),
        )


async def _handle_auto_msg_save(client: Client, message: Message) -> None:
    """Save the admin's message as the auto-message and return a deep link."""
    user_states.pop(ADMIN_ID, None)
    async with AsyncSessionLocal() as session:
        lang = await get_user_lang(session, ADMIN_ID)

    # Determine message type and relevant ID
    if message.text:
        payload = {"type": "text", "text": message.text}
    elif message.photo:
        payload = {"type": "photo",     "file_id": message.photo.file_id,
                   "caption": message.caption or ""}
    elif message.video:
        payload = {"type": "video",     "file_id": message.video.file_id,
                   "caption": message.caption or ""}
    elif message.document:
        payload = {"type": "document",  "file_id": message.document.file_id,
                   "caption": message.caption or ""}
    elif message.audio:
        payload = {"type": "audio",     "file_id": message.audio.file_id,
                   "caption": message.caption or ""}
    elif message.voice:
        payload = {"type": "voice",     "file_id": message.voice.file_id,
                   "caption": message.caption or ""}
    elif message.animation:
        payload = {"type": "animation", "file_id": message.animation.file_id,
                   "caption": message.caption or ""}
    elif message.video_note:
        payload = {"type": "video_note","file_id": message.video_note.file_id}
    elif message.sticker:
        payload = {"type": "sticker",   "file_id": message.sticker.file_id}
    else:
        await message.reply("❌ Unsupported message type. Please send text, photo, video, file, or audio.")
        return

    async with AsyncSessionLocal() as session:
        await set_setting(session, "auto_message", json.dumps(payload, ensure_ascii=False))

    link = f"https://t.me/{bot_info.BOT_USERNAME}?start=autostart"
    await message.reply(
        t("admin_auto_msg_saved", lang).format(link=link),
        reply_markup=admin_auto_msg_menu(has_msg=True, lang=lang),
        disable_web_page_preview=True,
    )


def _format_users_table(users: list, lang: str) -> str:
    """Format a compact user list as readable text."""
    if not users:
        return "—"
    lines = []
    for u in users:
        name = (u.first_name or "")[:16] or "—"
        uname = f"@{u.username}" if u.username else "—"
        drive = "✅" if u.has_personal_drive else "❌"
        if u.is_admin or u.upload_limit_exempt or u.referral_unlocked:
            plan = "⭐ Premium"
        else:
            plan = "· Normal"
        lines.append(f"`{u.id}` **{name}** {uname}\nDrive: {drive} | {plan}")
    return "\n\n".join(lines)


async def _show_user_info(query: CallbackQuery, target_id: int, lang: str) -> None:
    async with AsyncSessionLocal() as session:
        user = await session.get(User, target_id)
        if not user:
            await query.message.edit_text(t("admin_user_not_found", lang))
            return
        refs = await get_referral_count(session, target_id)
        info = t("admin_user_info", lang).format(
            id=user.id,
            name=user.first_name or "-",
            username=user.username or "-",
            lang=user.language or "-",
            joined=str(user.joined_at)[:10] if user.joined_at else "-",
            drive="✅" if user.has_personal_drive else "❌",
            is_admin="✅" if user.is_admin else "❌",
            exempt="✅" if user.upload_limit_exempt else "❌",
            refs=refs,
            daily_count=user.daily_upload_count or 0,
            daily_size=format_bytes(user.daily_upload_bytes or 0),
        )

    await query.message.edit_text(
        info,
        reply_markup=admin_user_actions(
            target_id, lang,
            is_admin_flag=bool(user.is_admin),
            is_exempt=bool(user.upload_limit_exempt),
        ),
    )
