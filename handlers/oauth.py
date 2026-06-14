"""
OAuth2 flow for linking a user's personal Google Drive (mandatory for uploads).

Flow:
  1. User taps "Authenticate Google Drive" → bot sends auth URL
  2. User opens URL, authorizes, is redirected to http://localhost?code=...
     (page fails to load — expected)
  3. User copies the full redirect URL from the browser address bar and sends it
  4. Bot extracts the code, exchanges it for tokens, and saves them to the DB
"""
import asyncio
import logging
from urllib.parse import parse_qs, urlparse

import asyncio

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message
from sqlalchemy import select

from config import ADMIN_ID, AUTO_OAUTH, GOOGLE_OAUTH_CLIENT_ID
from database.models import Upload, User as UserModel
from database.session import AsyncSessionLocal
from services.drive_service import create_oauth_flow, get_auth_url, build_user_service
from services.oauth_server import make_state
from utils.helpers import check_drive_status, get_drive_storage_info, get_or_create_user, get_user_lang
from utils.keyboards import back_to_main, cancel_action, confirm_delete_drive_data, drive_status_menu, drive_storage_result, main_menu
from utils.progress import format_bytes
from utils.state import UserState, oauth_flows, user_states
from utils.strings import t

logger = logging.getLogger(__name__)


def register(app: Client) -> None:

    # ── Link / Authenticate Drive ──────────────────────────────────────────────

    @app.on_callback_query(filters.regex("^link_drive$"))
    async def cb_link_drive(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)

        if not GOOGLE_OAUTH_CLIENT_ID:
            await query.answer(t("oauth_not_configured", lang), show_alert=True)
            return

        flow = create_oauth_flow()
        oauth_flows[user_id] = flow

        if AUTO_OAUTH:
            state_token = make_state(user_id)
            auth_url = get_auth_url(flow, state=state_token)
            instructions_key = "oauth_instructions_auto"
            # No WAITING_OAUTH_CODE state needed — callback server handles it
        else:
            auth_url = get_auth_url(flow)
            instructions_key = "oauth_instructions"
            user_states[user_id] = UserState.WAITING_OAUTH_CODE

        instructions = t(instructions_key, lang).format(auth_url=auth_url)
        await query.message.edit_text(
            f"{t('oauth_title', lang)}\n\n{instructions}",
            disable_web_page_preview=True,
            reply_markup=cancel_action(lang),
        )

    @app.on_callback_query(filters.regex("^drive_status$"))
    async def cb_drive_status(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)
            user = await session.get(UserModel, user_id)

        if not user or not user.has_personal_drive:
            await query.message.edit_text(
                t("drive_status_text", lang),
                reply_markup=drive_status_menu(lang),
            )
            return

        await query.message.edit_text(t("drive_status_checking", lang))
        result = await check_drive_status(user.oauth_access_token, user.oauth_refresh_token)

        if result["ok"]:
            text = t("drive_status_ok", lang)
        else:
            text = t("drive_status_error", lang).format(error=result["error"] or "unknown")

        await query.message.edit_text(text, reply_markup=drive_status_menu(lang))

    @app.on_callback_query(filters.regex("^drive_status_check$"))
    async def cb_drive_status_check(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)
            user = await session.get(UserModel, user_id)

        if not user or not user.has_personal_drive:
            await query.answer(t("drive_status_text", lang)[:200], show_alert=True)
            return

        await query.message.edit_text(t("drive_status_checking", lang))
        result = await check_drive_status(user.oauth_access_token, user.oauth_refresh_token)

        if result["ok"]:
            text = t("drive_status_ok", lang)
        else:
            text = t("drive_status_error", lang).format(error=result["error"] or "unknown")

        await query.message.edit_text(text, reply_markup=drive_status_menu(lang))

    # ── Drive storage usage ────────────────────────────────────────────────────

    @app.on_callback_query(filters.regex("^drive_storage$"))
    async def cb_drive_storage(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)
            user = await session.get(UserModel, user_id)

        if not user or not user.has_personal_drive:
            await query.answer(t("auth_required", lang)[:200], show_alert=True)
            return

        await query.message.edit_text(t("drive_storage_checking", lang))
        info = await get_drive_storage_info(user.oauth_access_token, user.oauth_refresh_token)

        if not info["ok"]:
            await query.message.edit_text(
                t("drive_storage_error", lang).format(error=info["error"]),
                reply_markup=drive_storage_result(lang),
            )
            return

        def _bar(pct: float, width: int = 12) -> str:
            filled = round(pct / 100 * width)
            return "█" * filled + "░" * (width - filled)

        usage_str = format_bytes(info["usage_bytes"])
        limit_str  = format_bytes(info["limit_bytes"])
        pct        = info["pct"]

        await query.message.edit_text(
            t("drive_storage_info", lang).format(
                usage=usage_str,
                limit=limit_str,
                bar=_bar(pct),
                pct=pct,
            ),
            reply_markup=drive_storage_result(lang),
        )

    # ── Unlink Drive ───────────────────────────────────────────────────────────

    @app.on_callback_query(filters.regex("^unlink_drive$"))
    async def cb_unlink_drive(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)
            user = await session.get(UserModel, user_id)
            if user:
                user.has_personal_drive = False
                user.oauth_access_token = None
                user.oauth_refresh_token = None
                user.oauth_token_expiry = None
                await session.commit()

        await query.message.edit_text(
            t("drive_unlinked", lang),
            reply_markup=back_to_main(lang),
        )

    # ── Delete all Drive data ──────────────────────────────────────────────────

    @app.on_callback_query(filters.regex("^delete_drive_data$"))
    async def cb_delete_drive_data(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)

        await query.message.edit_text(
            t("delete_drive_data_prompt", lang),
            reply_markup=confirm_delete_drive_data(lang),
        )

    @app.on_callback_query(filters.regex("^delete_drive_data_yes$"))
    async def cb_delete_drive_data_yes(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)
            user = await session.get(UserModel, user_id)

        await query.answer()
        await query.message.edit_text("🗑 Deleting…" if lang == "en" else "🗑 در حال حذف…")

        deleted = 0
        failed  = 0

        # ── Try to delete each file from Google Drive ──────────────────────
        if user and user.has_personal_drive and user.oauth_access_token:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Upload).where(
                        Upload.user_id == user_id,
                        Upload.is_personal_drive.is_(True),
                        Upload.is_deleted.is_(False),
                    )
                )
                uploads = result.scalars().all()

            if uploads:
                loop = asyncio.get_event_loop()
                try:
                    service, _ = build_user_service(
                        user.oauth_access_token, user.oauth_refresh_token
                    )
                except Exception:
                    service = None

                for upload in uploads:
                    if service:
                        try:
                            await loop.run_in_executor(
                                None,
                                lambda fid=upload.gdrive_file_id: (
                                    service.files().delete(fileId=fid).execute()
                                ),
                            )
                            deleted += 1
                        except Exception:
                            failed += 1
                    else:
                        failed += 1

        # ── Mark all uploads as deleted in DB + clear OAuth tokens ─────────
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Upload).where(Upload.user_id == user_id, Upload.is_deleted.is_(False))
            )
            for upload in result.scalars().all():
                upload.is_deleted = True

            db_user = await session.get(UserModel, user_id)
            if db_user:
                db_user.has_personal_drive    = False
                db_user.oauth_access_token    = None
                db_user.oauth_refresh_token   = None
                db_user.oauth_token_expiry    = None
                db_user.daily_upload_bytes    = 0
                db_user.daily_upload_count    = 0
            await session.commit()

        if failed == 0:
            text = t("delete_drive_data_done", lang)
        else:
            text = t("delete_drive_data_partial", lang).format(
                deleted=deleted, failed=failed
            )

        await query.message.edit_text(text, reply_markup=back_to_main(lang))

    # ── Cancel OAuth flow ──────────────────────────────────────────────────────

    @app.on_callback_query(filters.regex("^cancel_action$"))
    async def cb_cancel_action(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        state = user_states.pop(user_id, None)
        if state == UserState.WAITING_OAUTH_CODE:
            oauth_flows.pop(user_id, None)

        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(session, query.from_user)
            lang = user.language or "en"
            is_admin = user_id == ADMIN_ID or bool(user.is_admin)

        await query.message.edit_text(
            t("action_cancelled", lang),
            reply_markup=main_menu(lang=lang, is_admin=is_admin,
                                   has_personal_drive=user.has_personal_drive),
        )

    # ── Receive the redirect URL / auth code from the user ─────────────────────

    @app.on_message(filters.private & filters.text & ~filters.command(["start"]))
    async def handle_oauth_code(client: Client, message: Message):
        user_id = message.from_user.id
        if user_states.get(user_id) != UserState.WAITING_OAUTH_CODE:
            return

        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, user_id)

        flow = oauth_flows.get(user_id)
        if not flow:
            await message.reply(t("oauth_expired", lang))
            user_states.pop(user_id, None)
            return

        code = _extract_code(message.text.strip())
        if not code:
            await message.reply(t("oauth_code_hint", lang))
            return

        status = await message.reply(t("oauth_processing", lang))
        try:
            raw_url = message.text.strip()
            loop = asyncio.get_event_loop()
            # fetch_token is a blocking HTTP call — run it off the event loop
            if raw_url.startswith("http"):
                await loop.run_in_executor(
                    None, lambda: flow.fetch_token(authorization_response=raw_url)
                )
            else:
                await loop.run_in_executor(
                    None, lambda: flow.fetch_token(code=raw_url)
                )
            creds = flow.credentials

            async with AsyncSessionLocal() as session:
                user = await get_or_create_user(session, message.from_user)
                user.oauth_access_token = creds.token
                user.oauth_refresh_token = creds.refresh_token
                user.oauth_token_expiry = creds.expiry
                user.has_personal_drive = True
                await session.commit()
                await session.refresh(user)

            oauth_flows.pop(user_id, None)
            user_states.pop(user_id, None)

            is_admin = user_id == ADMIN_ID
            await status.edit_text(
                t("oauth_success", lang),
                reply_markup=main_menu(lang=lang, is_admin=is_admin, has_personal_drive=True),
            )

        except Exception as exc:
            logger.exception("OAuth token exchange failed for user %s", user_id)
            oauth_flows.pop(user_id, None)
            user_states.pop(user_id, None)
            await status.edit_text(
                t("oauth_failed", lang).format(error=str(exc)[:200])
            )


def _extract_code(text: str) -> str | None:
    """Extract the OAuth2 code from a redirect URL or a bare code string."""
    try:
        parsed = urlparse(text)
        params = parse_qs(parsed.query)
        codes = params.get("code")
        if codes:
            return codes[0]
    except Exception:
        pass
    # Bare code (Google codes typically start with "4/")
    if len(text) > 10:
        return text
    return None
