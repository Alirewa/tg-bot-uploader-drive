"""
Lightweight aiohttp server that catches Google OAuth2 callbacks automatically.

When GOOGLE_OAUTH_REDIRECT_URI is set to http://SERVER_IP:PORT/oauth/callback
(instead of http://localhost), the user only needs to click the auth link and
approve — the bot receives the code automatically and sends a success message.

Set OAUTH_SERVER_PORT in .env (default 8080) and open that port in the firewall.
"""
import asyncio
import logging
import secrets

from aiohttp import web

logger = logging.getLogger(__name__)

_pending: dict[str, int] = {}   # state_token → telegram user_id
_bot_app = None                  # Pyrogram Client, set at startup

_HTML_OK = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Connected!</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
       background:#f0f4f8;display:flex;align-items:center;justify-content:center;
       min-height:100vh;padding:20px}
  .card{background:#fff;border-radius:16px;padding:48px 40px;max-width:440px;
        width:100%;box-shadow:0 4px 24px rgba(0,0,0,.08);text-align:center}
  .icon{font-size:3.5rem;margin-bottom:16px}
  h1{color:#1a1a2e;font-size:1.6rem;margin-bottom:12px}
  p{color:#555;font-size:1rem;line-height:1.6}
  .sub{margin-top:20px;font-size:.875rem;color:#888}
</style></head>
<body><div class="card">
  <div class="icon">✅</div>
  <h1>Google Drive Connected!</h1>
  <p>Your account has been successfully linked to the bot.</p>
  <p>You can now <strong>close this tab</strong> and return to Telegram.</p>
  <p class="sub">The bot has already sent you a confirmation message.</p>
</div></body></html>"""

_HTML_ERR = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Error</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
       background:#f0f4f8;display:flex;align-items:center;justify-content:center;
       min-height:100vh;padding:20px}
  .card{background:#fff;border-radius:16px;padding:48px 40px;max-width:440px;
        width:100%;box-shadow:0 4px 24px rgba(0,0,0,.08);text-align:center}
  .icon{font-size:3.5rem;margin-bottom:16px}
  h1{color:#c0392b;font-size:1.6rem;margin-bottom:12px}
  p{color:#555;font-size:1rem;line-height:1.6}
  code{background:#f8f8f8;padding:4px 8px;border-radius:6px;font-size:.85rem;word-break:break-all}
</style></head>
<body><div class="card">
  <div class="icon">❌</div>
  <h1>Authentication Failed</h1>
  <p>{message}</p>
  <p style="margin-top:16px">Please return to Telegram and try again.</p>
</div></body></html>"""


def set_bot_app(app) -> None:
    global _bot_app
    _bot_app = app


def make_state(user_id: int) -> str:
    """Generate a random state token and map it to the user_id."""
    token = secrets.token_urlsafe(20)
    _pending[token] = user_id
    return token


async def _handle_callback(request: web.Request) -> web.Response:
    code  = request.query.get("code")
    state = request.query.get("state")
    error = request.query.get("error")

    if error:
        return web.Response(
            text=_HTML_ERR.format(message=f"Authorization denied: <code>{error}</code>"),
            content_type="text/html", status=400,
        )

    if not code or not state:
        return web.Response(
            text=_HTML_ERR.format(message="Missing required parameters."),
            content_type="text/html", status=400,
        )

    user_id = _pending.pop(state, None)
    if user_id is None:
        return web.Response(
            text=_HTML_ERR.format(
                message="Session expired or already used.<br>Please start the authentication again in Telegram."
            ),
            content_type="text/html", status=400,
        )

    from utils.state import oauth_flows, user_states
    flow = oauth_flows.get(user_id)
    if not flow:
        return web.Response(
            text=_HTML_ERR.format(message="OAuth session not found. Please try again."),
            content_type="text/html", status=400,
        )

    try:
        # Use the code directly instead of the full URL.
        # When running behind an nginx reverse proxy the URL aiohttp sees is
        # http://127.0.0.1:8080/... which doesn't match the registered redirect
        # URI (https://...). Passing the code alone avoids that mismatch —
        # google-auth-oauthlib sends the configured redirect_uri in the token
        # request body automatically.
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, lambda: flow.fetch_token(code=code)
        )
        creds = flow.credentials

        from database.session import AsyncSessionLocal
        from database.models import User as UserModel

        async with AsyncSessionLocal() as session:
            user = await session.get(UserModel, user_id)
            if user:
                user.oauth_access_token  = creds.token
                user.oauth_refresh_token = creds.refresh_token
                user.oauth_token_expiry  = creds.expiry
                user.has_personal_drive  = True
                await session.commit()

        oauth_flows.pop(user_id, None)
        user_states.pop(user_id, None)

        if _bot_app:
            from utils.strings import t
            from utils.keyboards import main_menu
            from utils.helpers import get_user_lang
            from config import ADMIN_ID
            async with AsyncSessionLocal() as session:
                lang     = await get_user_lang(session, user_id)
                u        = await session.get(UserModel, user_id)
                is_admin = user_id == ADMIN_ID or (bool(u.is_admin) if u else False)
            try:
                await _bot_app.send_message(
                    user_id,
                    t("oauth_success", lang),
                    reply_markup=main_menu(lang=lang, is_admin=is_admin, has_personal_drive=True),
                )
            except Exception:
                pass

        return web.Response(text=_HTML_OK, content_type="text/html")

    except Exception as exc:
        logger.exception("OAuth callback failed for user %s", user_id)
        oauth_flows.pop(user_id, None)
        user_states.pop(user_id, None)

        if _bot_app:
            try:
                from utils.strings import t
                from utils.helpers import get_user_lang
                from database.session import AsyncSessionLocal
                async with AsyncSessionLocal() as session:
                    lang = await get_user_lang(session, user_id)
                await _bot_app.send_message(
                    user_id,
                    t("oauth_failed", lang).format(error=str(exc)[:200]),
                )
            except Exception:
                pass

        return web.Response(
            text=_HTML_ERR.format(message=f"<code>{str(exc)[:300]}</code>"),
            content_type="text/html", status=500,
        )


async def start_oauth_server(port: int) -> None:
    aio_app = web.Application()
    aio_app.router.add_get("/oauth/callback", _handle_callback)
    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info("OAuth callback server listening on 0.0.0.0:%d", port)
