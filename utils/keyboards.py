from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.strings import t


def language_selection() -> InlineKeyboardMarkup:
    """Shown once on first /start — user picks EN or FA."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🇬🇧  English", callback_data="set_lang_en"),
        InlineKeyboardButton("🇮🇷  فارسی",   callback_data="set_lang_fa"),
    ]])


def main_menu(lang: str = "en", is_admin: bool = False,
              has_personal_drive: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t("btn_upload_info", lang), callback_data="upload_info")],
    ]
    if has_personal_drive:
        rows.append([InlineKeyboardButton(t("btn_drive_linked", lang), callback_data="drive_status")])
    else:
        rows.append([InlineKeyboardButton(t("btn_link_drive", lang), callback_data="link_drive")])

    rows.append([InlineKeyboardButton(t("btn_my_stats", lang), callback_data="my_stats")])

    if is_admin:
        rows.append([InlineKeyboardButton(t("btn_admin_panel", lang), callback_data="admin_panel")])

    return InlineKeyboardMarkup(rows)


def admin_panel(lang: str = "en", bot_on: bool = True) -> InlineKeyboardMarkup:
    toggle_label = t("btn_bot_off", lang) if bot_on else t("btn_bot_on", lang)
    toggle_data  = "admin_bot_off"        if bot_on else "admin_bot_on"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_admin_stats",     lang), callback_data="admin_stats")],
        [InlineKeyboardButton(t("btn_admin_broadcast", lang), callback_data="admin_broadcast")],
        [InlineKeyboardButton(toggle_label,                   callback_data=toggle_data)],
        [InlineKeyboardButton(t("btn_back_main",       lang), callback_data="main_menu")],
    ])


def force_join(channels: list[str], lang: str = "en") -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(f"📢  {ch}", url=f"https://t.me/{ch.lstrip('@')}")]
        for ch in channels
    ]
    rows.append([InlineKeyboardButton(t("btn_check_join", lang), callback_data="check_join")])
    return InlineKeyboardMarkup(rows)


def drive_status_menu(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_relink_drive", lang), callback_data="link_drive")],
        [InlineKeyboardButton(t("btn_unlink_drive", lang), callback_data="unlink_drive")],
        [InlineKeyboardButton(t("btn_back_main",    lang), callback_data="main_menu")],
    ])


def authenticate_button(lang: str = "en") -> InlineKeyboardMarkup:
    """Single-button keyboard prompting OAuth authentication."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t("btn_authenticate", lang), callback_data="link_drive")
    ]])


def cancel_action(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t("btn_cancel", lang), callback_data="cancel_action")
    ]])


def back_to_main(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t("btn_back_main", lang), callback_data="main_menu")
    ]])
