from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove,
)
from utils.strings import t


# ── Persistent reply keyboard (always-visible bottom bar) ────────────────────

def reply_main_menu(lang: str = "en") -> ReplyKeyboardMarkup:
    """Bottom persistent keyboard — shown on /start."""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(t("rbtn_upload", lang)), KeyboardButton(t("rbtn_my_drive", lang))],
            [KeyboardButton(t("rbtn_stats",  lang)), KeyboardButton(t("rbtn_referral", lang))],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def remove_reply_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def language_selection() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🇬🇧  English", callback_data="set_lang_en"),
        InlineKeyboardButton("🇮🇷  فارسی",   callback_data="set_lang_fa"),
    ]])


def main_menu(lang: str = "en", is_admin: bool = False,
              has_personal_drive: bool = False) -> InlineKeyboardMarkup:
    rows = []
    if has_personal_drive:
        rows.append([InlineKeyboardButton(t("btn_drive_linked", lang), callback_data="drive_status")])
    else:
        rows.append([InlineKeyboardButton(t("btn_link_drive", lang), callback_data="link_drive")])

    rows.append([InlineKeyboardButton(t("btn_drive_to_tg", lang), callback_data="drive_to_tg")])
    rows.append([InlineKeyboardButton(t("btn_my_stats",   lang), callback_data="my_stats")])
    rows.append([InlineKeyboardButton(t("btn_referral",   lang), callback_data="referral")])

    if is_admin:
        rows.append([InlineKeyboardButton(t("btn_admin_panel", lang), callback_data="admin_panel")])

    return InlineKeyboardMarkup(rows)


def admin_panel(lang: str = "en", bot_on: bool = True) -> InlineKeyboardMarkup:
    toggle_label = t("btn_bot_off", lang) if bot_on else t("btn_bot_on", lang)
    toggle_data  = "admin_bot_off"        if bot_on else "admin_bot_on"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_admin_stats",     lang), callback_data="admin_stats")],
        [InlineKeyboardButton(t("btn_admin_broadcast", lang), callback_data="admin_broadcast")],
        [InlineKeyboardButton(t("btn_admin_users",     lang), callback_data="admin_users")],
        [InlineKeyboardButton(t("btn_admin_channels",  lang), callback_data="admin_channels")],
        [InlineKeyboardButton(t("btn_admin_auto_msg",  lang), callback_data="admin_auto_msg")],
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
        [InlineKeyboardButton(t("btn_drive_storage",      lang), callback_data="drive_storage")],
        [InlineKeyboardButton(t("btn_check_drive_status", lang), callback_data="drive_status_check")],
        [InlineKeyboardButton(t("btn_relink_drive",       lang), callback_data="link_drive")],
        [InlineKeyboardButton(t("btn_unlink_drive",       lang), callback_data="unlink_drive")],
        [InlineKeyboardButton(t("btn_delete_drive_data",  lang), callback_data="delete_drive_data")],
        [InlineKeyboardButton(t("btn_back_main",          lang), callback_data="main_menu")],
    ])


def confirm_delete_drive_data(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_confirm_delete_yes", lang), callback_data="delete_drive_data_yes")],
        [InlineKeyboardButton(t("btn_confirm_delete_no",  lang), callback_data="drive_status")],
    ])


def drive_storage_result(lang: str = "en") -> InlineKeyboardMarkup:
    """Keyboard shown after displaying Drive storage info."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_open_drive", lang), url="https://drive.google.com/drive/quota")],
        [InlineKeyboardButton(t("btn_back_main",  lang), callback_data="drive_status")],
    ])


def authenticate_button(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t("btn_authenticate", lang), callback_data="link_drive")
    ]])


def drive_selection(lang: str = "en", has_personal_drive: bool = False,
                    bot_drive_full: bool = False) -> InlineKeyboardMarkup:
    rows = []
    if has_personal_drive:
        rows.append([InlineKeyboardButton(t("btn_use_my_drive", lang), callback_data="upload_to_personal")])
    else:
        rows.append([InlineKeyboardButton(t("btn_authenticate_upload", lang), callback_data="upload_auth_then")])
    if bot_drive_full:
        rows.append([InlineKeyboardButton(t("btn_bot_drive_full", lang), callback_data="bot_drive_full_info")])
    else:
        rows.append([InlineKeyboardButton(t("btn_use_bot_drive", lang), callback_data="upload_to_bot")])
    rows.append([InlineKeyboardButton(t("btn_cancel", lang), callback_data="cancel_upload")])
    return InlineKeyboardMarkup(rows)


def dest_selection(lang: str = "en") -> InlineKeyboardMarkup:
    """Drive vs Telegram destination picker shown after platform detection."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_dest_telegram", lang), callback_data="dest_telegram")],
        [InlineKeyboardButton(t("btn_dest_drive",    lang), callback_data="dest_drive")],
        [InlineKeyboardButton(t("btn_cancel",        lang), callback_data="cancel_upload")],
    ])


def yt_quality_menu(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_ytq_best",  lang), callback_data="ytq_best")],
        [InlineKeyboardButton(t("btn_ytq_720",   lang), callback_data="ytq_720"),
         InlineKeyboardButton(t("btn_ytq_480",   lang), callback_data="ytq_480")],
        [InlineKeyboardButton(t("btn_ytq_audio", lang), callback_data="ytq_audio")],
        [InlineKeyboardButton(t("btn_cancel",    lang), callback_data="cancel_upload")],
    ])


def cancel_action(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t("btn_cancel", lang), callback_data="cancel_action")
    ]])


def back_to_main(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(t("btn_back_main", lang), callback_data="main_menu")
    ]])


def referral_menu(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_referral",  lang), callback_data="referral")],
        [InlineKeyboardButton(t("btn_back_main", lang), callback_data="main_menu")],
    ])


_PAGE_SIZE = 10


def admin_users_list(users: list, page: int, total: int, lang: str) -> InlineKeyboardMarkup:
    """Paginated user list keyboard for admin panel."""
    rows = []
    for u in users:
        name = (u.first_name or "")[:18] or str(u.id)
        plan = "⭐" if (u.referral_unlocked or u.upload_limit_exempt or u.is_admin) else "·"
        drive = "✅" if u.has_personal_drive else "❌"
        label = f"{plan} {name} {drive}"
        rows.append([InlineKeyboardButton(label, callback_data=f"admin_view_user_{u.id}")])

    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"admin_users_page_{page - 1}"))
    pages = max(1, (total + _PAGE_SIZE - 1) // _PAGE_SIZE)
    nav.append(InlineKeyboardButton(f"{page + 1}/{pages}", callback_data="noop"))
    if (page + 1) * _PAGE_SIZE < total:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"admin_users_page_{page + 1}"))
    rows.append(nav)

    rows.append([InlineKeyboardButton(t("btn_search_user", lang), callback_data="admin_user_search")])
    rows.append([InlineKeyboardButton(t("btn_back_admin",  lang), callback_data="admin_panel")])
    return InlineKeyboardMarkup(rows)


def admin_user_actions(user_id: int, lang: str, is_admin_flag: bool, is_exempt: bool) -> InlineKeyboardMarkup:
    rows = []
    if is_admin_flag:
        rows.append([InlineKeyboardButton(t("btn_remove_admin", lang), callback_data=f"admin_rm_admin_{user_id}")])
    else:
        rows.append([InlineKeyboardButton(t("btn_make_admin", lang), callback_data=f"admin_mk_admin_{user_id}")])
    if is_exempt:
        rows.append([InlineKeyboardButton(t("btn_revoke_exempt", lang), callback_data=f"admin_revoke_exempt_{user_id}")])
    else:
        rows.append([InlineKeyboardButton(t("btn_grant_exempt", lang), callback_data=f"admin_grant_exempt_{user_id}")])
    rows.append([InlineKeyboardButton("◀️  " + t("btn_admin_users", lang), callback_data="admin_users")])
    rows.append([InlineKeyboardButton(t("btn_back_admin", lang), callback_data="admin_panel")])
    return InlineKeyboardMarkup(rows)


def admin_auto_msg_menu(has_msg: bool, lang: str = "en") -> InlineKeyboardMarkup:
    rows = []
    if has_msg:
        rows.append([InlineKeyboardButton(t("btn_auto_msg_clear", lang), callback_data="admin_auto_msg_clear")])
    rows.append([InlineKeyboardButton(t("btn_back_admin", lang), callback_data="admin_panel")])
    return InlineKeyboardMarkup(rows)


def admin_channels_menu(channels: list[str], lang: str = "en") -> InlineKeyboardMarkup:
    rows = []
    for ch in channels:
        rows.append([
            InlineKeyboardButton(ch, url=f"https://t.me/{ch.lstrip('@')}"),
            InlineKeyboardButton(f"🗑 {t('btn_remove_channel', lang)}", callback_data=f"admin_rm_ch_{ch.lstrip('@')}"),
        ])
    rows.append([InlineKeyboardButton(t("btn_add_channel", lang), callback_data="admin_add_channel")])
    rows.append([InlineKeyboardButton(t("btn_back_admin", lang), callback_data="admin_panel")])
    return InlineKeyboardMarkup(rows)
