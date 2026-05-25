"""
Admin panel — bilingual, no service-account management.

Actions:
  • Bot statistics (users, uploads, stored data)
  • Broadcast message to all users
  • Turn bot on / off
"""
import asyncio
import logging

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message
from sqlalchemy import func, select

from config import ADMIN_ID
from database.models import Upload, User
from database.session import AsyncSessionLocal
from utils.helpers import get_setting, get_user_lang, set_setting
from utils.keyboards import admin_panel, back_to_main, cancel_action, main_menu
from utils.progress import format_bytes
from utils.state import UserState, user_states
from utils.strings import t

logger = logging.getLogger(__name__)

_ADMIN = filters.user(ADMIN_ID) & filters.private


def register(app: Client) -> None:

    # ── Admin panel ────────────────────────────────────────────────────────────

    @app.on_callback_query(_ADMIN & filters.regex("^admin_panel$"))
    async def cb_admin_panel(client: Client, query: CallbackQuery):
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)
            status = await get_setting(session, "bot_status", "on")
        await query.message.edit_text(
            t("admin_panel_title", lang),
            reply_markup=admin_panel(lang=lang, bot_on=(status == "on")),
        )

    # ── Statistics ─────────────────────────────────────────────────────────────

    @app.on_callback_query(_ADMIN & filters.regex("^admin_stats$"))
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

    # ── Broadcast ─────────────────────────────────────────────────────────────

    @app.on_callback_query(_ADMIN & filters.regex("^admin_broadcast$"))
    async def cb_broadcast_prompt(client: Client, query: CallbackQuery):
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)
        user_states[ADMIN_ID] = UserState.WAITING_BROADCAST
        await query.message.edit_text(
            t("broadcast_prompt", lang),
            reply_markup=cancel_action(lang),
        )

    @app.on_message(_ADMIN & ~filters.command(["start"]))
    async def handle_admin_input(client: Client, message: Message):
        """Routes admin text/media to the broadcast flow when in WAITING_BROADCAST state."""
        if user_states.get(ADMIN_ID) == UserState.WAITING_BROADCAST:
            await _do_broadcast(client, message)

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
                await asyncio.sleep(0.05)  # ~20 msgs/s — Telegram limit buffer
            except Exception:
                failed += 1

        await status.edit_text(
            t("broadcast_done", lang).format(ok=f"{success:,}", fail=f"{failed:,}")
        )

    # ── Bot on / off ───────────────────────────────────────────────────────────

    @app.on_callback_query(_ADMIN & filters.regex("^admin_bot_(on|off)$"))
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

    # ── Cancel (admin context) ─────────────────────────────────────────────────

    @app.on_callback_query(_ADMIN & filters.regex("^cancel_action$"))
    async def cb_cancel_admin(client: Client, query: CallbackQuery):
        user_states.pop(ADMIN_ID, None)
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, ADMIN_ID)
            status = await get_setting(session, "bot_status", "on")
        await query.message.edit_text(
            t("admin_panel_title", lang),
            reply_markup=admin_panel(lang=lang, bot_on=(status == "on")),
        )
