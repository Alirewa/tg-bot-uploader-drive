"""
OAuth2 flow for linking a user's personal Google Drive (mandatory for uploads).

Flow:
  1. User taps "Authenticate Google Drive" → bot sends auth URL
  2. User opens URL, authorizes, is redirected to http://localhost?code=...
     (page fails to load — expected)
  3. User copies the full redirect URL from the browser address bar and sends it
  4. Bot extracts the code, exchanges it for tokens, and saves them to the DB
"""
import logging
from urllib.parse import parse_qs, urlparse

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

from config import ADMIN_ID, GOOGLE_OAUTH_CLIENT_ID
from database.models import User as UserModel
from database.session import AsyncSessionLocal
from services.drive_service import create_oauth_flow, get_auth_url
from utils.helpers import get_or_create_user, get_user_lang
from utils.keyboards import back_to_main, cancel_action, drive_status_menu, main_menu
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
        auth_url = get_auth_url(flow)
        oauth_flows[user_id] = flow
        user_states[user_id] = UserState.WAITING_OAUTH_CODE

        instructions = t("oauth_instructions", lang).format(auth_url=auth_url)
        await query.message.edit_text(
            f"{t('oauth_title', lang)}\n\n{instructions}",
            disable_web_page_preview=True,
            reply_markup=cancel_action(lang),
        )

    # ── Drive status page ──────────────────────────────────────────────────────

    @app.on_callback_query(filters.regex("^drive_status$"))
    async def cb_drive_status(client: Client, query: CallbackQuery):
        async with AsyncSessionLocal() as session:
            lang = await get_user_lang(session, query.from_user.id)
        await query.message.edit_text(
            t("drive_status_text", lang),
            reply_markup=drive_status_menu(lang),
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

    # ── Cancel OAuth flow ──────────────────────────────────────────────────────

    @app.on_callback_query(filters.regex("^cancel_action$") & filters.private)
    async def cb_cancel_action(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        state = user_states.pop(user_id, None)
        if state == UserState.WAITING_OAUTH_CODE:
            oauth_flows.pop(user_id, None)

        async with AsyncSessionLocal() as session:
            user = await get_or_create_user(session, query.from_user)
            lang = user.language or "en"
            is_admin = user_id == ADMIN_ID

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
            flow.fetch_token(code=code)
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
