import logging

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message
from sqlalchemy import func, select

from config import ADMIN_ID
from database.models import Upload
from database.session import AsyncSessionLocal
from services.force_join import get_unjoined_channels
from utils.helpers import get_or_create_user, get_setting, get_user_lang
from utils.keyboards import back_to_main, force_join, language_selection, main_menu
from utils.progress import format_bytes
from utils.strings import t

logger = logging.getLogger(__name__)


def register(app: Client) -> None:

    # ── /start ────────────────────────────────────────────────────────────────

    @app.on_message(filters.command("start") & filters.private)
    async def cmd_start(client: Client, message: Message):
        async with AsyncSessionLocal() as session:
            bot_status = await get_setting(session, "bot_status", "on")

        if bot_status == "off" and message.from_user.id != ADMIN_ID:
            # Use both languages for the offline message since we don't know
            # their preference yet if they haven't selected one
            await message.reply(
                "🔴 Bot is under maintenance. / ربات در حال تعمیر است.\n\n"
                "Please try again later. / لطفاً بعداً تلاش کنید."
            )
            return

        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(session, message.from_user)
            lang = user.language

        # First visit — no language chosen yet
        if lang not in ("en", "fa"):
            await message.reply(
                t("choose_language", "en"),
                reply_markup=language_selection(),
            )
            return

        # Language already set — check force-join then show menu
        await _show_main_or_join(client, message, lang, message.from_user.id)

    # ── Language selection callbacks ───────────────────────────────────────────

    @app.on_callback_query(filters.regex(r"^set_lang_(en|fa)$"))
    async def cb_set_language(client: Client, query: CallbackQuery):
        lang = query.matches[0].group(1)
        user_id = query.from_user.id

        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(session, query.from_user)
            user.language = lang
            await session.commit()

        # Now check bot status again
        async with AsyncSessionLocal() as session:
            bot_status = await get_setting(session, "bot_status", "on")

        if bot_status == "off" and user_id != ADMIN_ID:
            await query.message.edit_text(t("bot_offline", lang))
            return

        await _show_main_or_join_query(client, query, lang, user_id)

    # ── Check join callback ────────────────────────────────────────────────────

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
            is_admin = user_id == ADMIN_ID
            await query.message.edit_text(
                t("welcome", lang),
                reply_markup=main_menu(lang=lang, is_admin=is_admin,
                                       has_personal_drive=user.has_personal_drive),
            )

    # ── Main menu callback ─────────────────────────────────────────────────────

    @app.on_callback_query(filters.regex("^main_menu$"))
    async def cb_main_menu(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(session, query.from_user)
            lang = user.language or "en"
            is_admin = user_id == ADMIN_ID
        await query.message.edit_text(
            t("welcome", lang),
            reply_markup=main_menu(lang=lang, is_admin=is_admin,
                                   has_personal_drive=user.has_personal_drive),
        )

    # ── Upload info hint ───────────────────────────────────────────────────────

    @app.on_callback_query(filters.regex("^upload_info$"))
    async def cb_upload_info(client: Client, query: CallbackQuery):
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, query.from_user.id)
        await query.answer(t("upload_hint", lang), show_alert=True)

    # ── My stats ───────────────────────────────────────────────────────────────

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


# ── Shared helpers ─────────────────────────────────────────────────────────────

async def _show_main_or_join(client: Client, message: Message, lang: str, user_id: int):
    unjoined = await get_unjoined_channels(client, user_id)
    if unjoined:
        await message.reply(
            t("force_join_prompt", lang),
            reply_markup=force_join(unjoined, lang),
        )
        return

    async with AsyncSessionLocal() as session:
        user = await session.get(__import__("database.models", fromlist=["User"]).User, user_id)
        is_admin = user_id == ADMIN_ID
        has_drive = user.has_personal_drive if user else False

    await message.reply(
        t("welcome", lang),
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
        from database.models import User as UserModel
        user = await session.get(UserModel, user_id)
        is_admin = user_id == ADMIN_ID
        has_drive = user.has_personal_drive if user else False

    await query.message.edit_text(
        t("welcome", lang),
        reply_markup=main_menu(lang=lang, is_admin=is_admin, has_personal_drive=has_drive),
    )
