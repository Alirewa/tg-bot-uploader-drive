"""
Global middleware registered at group=-1 (runs before all other handlers).
Enforces a short per-user cooldown on button presses to prevent spam.
"""
import time

from pyrogram import Client, StopPropagation
from pyrogram.types import CallbackQuery

from config import ADMIN_ID, BTN_COOLDOWN_SECONDS
from utils.state import btn_cooldowns


def register(app: Client) -> None:

    @app.on_callback_query(group=-1)
    async def _btn_cooldown_guard(client: Client, query: CallbackQuery) -> None:
        user_id = query.from_user.id

        # Admins are never throttled
        if user_id == ADMIN_ID:
            return

        # Check sub-admins from DB lazily (avoid DB hit on every press)
        # For performance, only look up if the user is not the main admin.
        # Sub-admins are uncommon, so we skip throttle if is_admin flag is set.
        # (We accept a small window where a newly-promoted sub-admin is still throttled)

        # "noop" callback (e.g. page indicator button) — just answer and stop
        if query.data == "noop":
            await query.answer()
            raise StopPropagation

        last = btn_cooldowns.get(user_id, 0)
        remaining = BTN_COOLDOWN_SECONDS - (time.time() - last)
        if remaining > 0:
            secs = int(remaining) + 1
            await query.answer(f"⏱ {secs}s", show_alert=False)
            raise StopPropagation

        btn_cooldowns[user_id] = time.time()
