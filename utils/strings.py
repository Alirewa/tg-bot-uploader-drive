"""
Bilingual string registry — English (en) and Persian/Farsi (fa).

Usage:
    from utils.strings import t
    text = t("welcome", lang)
"""

STRINGS: dict[str, dict[str, str]] = {
    # ─────────────────────────────────────────────────────────────────────────
    "en": {
        # ── Language selection ──────────────────────────────────────────────
        "choose_language":
            "🌐 Welcome! Please choose your language to continue:\n\n"
            "🌐 خوش آمدید! لطفاً زبان خود را برای ادامه انتخاب کنید:",
        "btn_english": "🇬🇧  English",
        "btn_persian": "🇮🇷  فارسی",

        # ── Welcome / main menu ─────────────────────────────────────────────
        "welcome":
            "👋 **Welcome to Drive Uploader Bot!**\n\n"
            "Send me any file (up to **2 GB**) and I'll upload it directly to "
            "your personal Google Drive and give you a shareable link.\n\n"
            "Use the buttons below to get started.",
        "btn_upload_info":    "📤  Send a File to Upload",
        "btn_link_drive":     "🔗  Authenticate Google Drive",
        "btn_drive_linked":   "✅  Google Drive Connected",
        "btn_my_stats":       "📊  My Upload Statistics",
        "btn_admin_panel":    "⚙️  Admin Panel",

        # ── Bot offline ─────────────────────────────────────────────────────
        "bot_offline":
            "🔴 **Bot Maintenance**\n\n"
            "The bot is temporarily offline. Please try again later.",

        # ── Force-join ──────────────────────────────────────────────────────
        "force_join_prompt":
            "⚠️ **Channel Membership Required**\n\n"
            "Please join our channels to use this bot:",
        "btn_check_join": "✅  I Joined — Check Again",

        # ── Auth required (mandatory OAuth gate) ────────────────────────────
        "auth_required":
            "Dear user, to use the upload feature, please authenticate your "
            "Google Drive account by clicking the button below.",
        "btn_authenticate": "🔗  Authenticate Google Drive",

        # ── OAuth instructions ──────────────────────────────────────────────
        "oauth_title": "🔗 **Authenticate Your Google Drive**",
        "oauth_instructions":
            "**Step 1 —** Click the link below to open Google's authorization page:\n"
            "{auth_url}\n\n"
            "**Step 2 —** Sign in with your Google account and grant the requested permission.\n\n"
            "**Step 3 —** After authorizing, Google will redirect you to a page that "
            "**won't load** — that is expected.\n\n"
            "**Step 4 —** Copy the **full URL** from your browser's address bar and paste "
            "it here.\n\n"
            "_The URL begins with_ `http://localhost/?code=`",
        "oauth_not_configured":
            "⚙️ **Personal Drive Not Configured**\n\n"
            "Google OAuth2 credentials are not set up on this bot instance. "
            "Please contact the administrator.",
        "oauth_processing":   "⏳ Exchanging authorization code…",
        "oauth_success":
            "✅ **Google Drive Authenticated!**\n\n"
            "Your personal Google Drive (15 GB) is now connected.\n"
            "You can now send files and they will be uploaded directly to your Drive.",
        "oauth_failed":
            "❌ **Authentication Failed**\n\n"
            "`{error}`\n\nPlease try authenticating again.",
        "oauth_code_hint":
            "❌ Could not find the authorization code.\n\n"
            "Please paste the **full URL** from your browser address bar.\n"
            "It looks like: `http://localhost/?code=4/XXXXXXX&scope=...`",
        "oauth_expired":
            "⚠️ OAuth session expired. Please start the authentication again.",
        "btn_authorize":  "🔐  Open Authorization Page",
        "btn_cancel":     "❌  Cancel",

        # ── Drive status ────────────────────────────────────────────────────
        "drive_status_text":
            "✅ **Google Drive Connected**\n\n"
            "Your personal Google Drive is linked to this bot.\n"
            "Your files are uploaded directly to your 15 GB storage.",
        "btn_relink_drive":  "🔄  Re-authenticate",
        "btn_unlink_drive":  "❌  Disconnect Google Drive",
        "drive_unlinked":
            "✅ **Google Drive Disconnected**\n\n"
            "Your account has been unlinked from this bot.",

        # ── Upload flow ─────────────────────────────────────────────────────
        "upload_starting":       "⏳ **Starting…**",
        "upload_hint":           "Just send me any file directly in this chat!",
        "upload_already_running":
            "⏳ You already have an upload in progress. Please wait for it to finish.",
        "upload_rate_limited":
            "🚫 **Slow Down!**\n\n"
            "You're uploading too fast. Please wait **{wait}s** and try again.",
        "upload_too_large":
            "❌ **File Too Large**\n\n"
            "Maximum allowed: **2 GB**\n"
            "Your file: **{size}**",
        "download_header":  "📥 **Downloading from Telegram…**",
        "upload_header":    "📤 **Uploading to Google Drive…**",
        "upload_complete":
            "✅ **Upload Complete!**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📄  **File:** `{name}`\n"
            "📦  **Size:** {size}\n\n"
            "🔗 **[Open / Download]({link})**",
        "upload_failed":
            "❌ **Upload Failed**\n\nSomething went wrong. Please try again.",

        # ── My stats ────────────────────────────────────────────────────────
        "my_stats":
            "📊 **Your Upload Statistics**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📤  Total uploads: **{total}**\n"
            "💾  Data stored: **{size}**",

        # ── Admin panel ─────────────────────────────────────────────────────
        "admin_panel_title":     "⚙️ **Admin Panel**\nChoose an action:",
        "btn_admin_stats":       "📊  Bot Statistics",
        "btn_admin_broadcast":   "📢  Broadcast Message",
        "btn_bot_off":           "🔴  Turn Bot OFF",
        "btn_bot_on":            "🟢  Turn Bot ON",
        "btn_back_main":         "◀️  Main Menu",
        "btn_back_admin":        "◀️  Admin Panel",

        "admin_stats":
            "📊 **Bot Statistics**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👥  Total users: **{users}**\n"
            "📤  Total uploads: **{uploads}**\n"
            "💾  Data stored: **{size}**",

        "broadcast_prompt":
            "📢 **Broadcast Message**\n\n"
            "Send the message you want to broadcast to all users.\n"
            "Supports text, photos, videos, documents, and audio.",
        "broadcast_sending":  "📢 Broadcasting…",
        "broadcast_done":
            "📢 **Broadcast Complete**\n\n"
            "✅  Delivered: **{ok}**\n"
            "❌  Failed: **{fail}**",

        "bot_toggled_on":   "✅ Bot is now ONLINE.",
        "bot_toggled_off":  "🔴 Bot is now OFFLINE (maintenance mode).",

        "action_cancelled": "✅ Action cancelled.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    "fa": {
        # ── Language selection ──────────────────────────────────────────────
        "choose_language":
            "🌐 Welcome! Please choose your language to continue:\n\n"
            "🌐 خوش آمدید! لطفاً زبان خود را برای ادامه انتخاب کنید:",
        "btn_english": "🇬🇧  English",
        "btn_persian": "🇮🇷  فارسی",

        # ── Welcome / main menu ─────────────────────────────────────────────
        "welcome":
            "👋 **به ربات آپلودر درایو خوش آمدید!**\n\n"
            "هر فایلی (تا **۲ گیگابایت**) برای من بفرستید تا مستقیماً در "
            "Google Drive شخصی شما آپلود کنم و لینک اشتراک‌گذاری بدهم.\n\n"
            "از دکمه‌های زیر شروع کنید.",
        "btn_upload_info":    "📤  ارسال فایل برای آپلود",
        "btn_link_drive":     "🔗  احراز هویت Google Drive",
        "btn_drive_linked":   "✅  Google Drive متصل است",
        "btn_my_stats":       "📊  آمار آپلودهای من",
        "btn_admin_panel":    "⚙️  پنل مدیریت",

        # ── Bot offline ─────────────────────────────────────────────────────
        "bot_offline":
            "🔴 **ربات در حال تعمیر است**\n\n"
            "ربات موقتاً آفلاین است. لطفاً بعداً تلاش کنید.",

        # ── Force-join ──────────────────────────────────────────────────────
        "force_join_prompt":
            "⚠️ **عضویت در کانال‌ها الزامی است**\n\n"
            "برای استفاده از ربات، لطفاً در کانال‌های ما عضو شوید:",
        "btn_check_join": "✅  عضو شدم — بررسی مجدد",

        # ── Auth required ────────────────────────────────────────────────────
        "auth_required":
            "کاربر عزیز، برای استفاده از قابلیت آپلود، لطفاً حساب "
            "Google Drive خود را با کلیک روی دکمه زیر احراز هویت کنید.",
        "btn_authenticate": "🔗  احراز هویت Google Drive",

        # ── OAuth instructions ──────────────────────────────────────────────
        "oauth_title": "🔗 **احراز هویت Google Drive شما**",
        "oauth_instructions":
            "**مرحله ۱ —** روی لینک زیر کلیک کنید تا صفحه مجوز گوگل باز شود:\n"
            "{auth_url}\n\n"
            "**مرحله ۲ —** با حساب Google خود وارد شوید و مجوز درخواستی را بدهید.\n\n"
            "**مرحله ۳ —** پس از تأیید، گوگل شما را به صفحه‌ای هدایت می‌کند که "
            "**بارگذاری نمی‌شود** — این طبیعی است.\n\n"
            "**مرحله ۴ —** **آدرس کامل URL** را از نوار آدرس مرورگر کپی کرده و "
            "اینجا بفرستید.\n\n"
            "_URL با_ `http://localhost/?code=` _شروع می‌شود_",
        "oauth_not_configured":
            "⚙️ **Google Drive پیکربندی نشده**\n\n"
            "اعتبارنامه‌های OAuth2 در این ربات تنظیم نشده‌اند. "
            "لطفاً با مدیر تماس بگیرید.",
        "oauth_processing":   "⏳ در حال تبادل کد مجوز…",
        "oauth_success":
            "✅ **Google Drive با موفقیت احراز هویت شد!**\n\n"
            "Google Drive شخصی شما (۱۵ گیگابایت) اکنون متصل است.\n"
            "می‌توانید فایل‌ها ارسال کنید تا مستقیماً در Drive شما آپلود شوند.",
        "oauth_failed":
            "❌ **احراز هویت ناموفق بود**\n\n"
            "`{error}`\n\nلطفاً دوباره تلاش کنید.",
        "oauth_code_hint":
            "❌ کد مجوز یافت نشد.\n\n"
            "لطفاً **آدرس کامل URL** از نوار آدرس مرورگر را بفرستید.\n"
            "شبیه این است: `http://localhost/?code=4/XXXXXXX&scope=...`",
        "oauth_expired":
            "⚠️ نشست OAuth منقضی شده. لطفاً دوباره احراز هویت کنید.",
        "btn_authorize":  "🔐  باز کردن صفحه مجوز",
        "btn_cancel":     "❌  لغو",

        # ── Drive status ────────────────────────────────────────────────────
        "drive_status_text":
            "✅ **Google Drive متصل است**\n\n"
            "Google Drive شخصی شما به این ربات متصل است.\n"
            "فایل‌های شما مستقیماً در فضای ۱۵ گیگابایتی شما آپلود می‌شوند.",
        "btn_relink_drive":  "🔄  احراز هویت مجدد",
        "btn_unlink_drive":  "❌  قطع اتصال Google Drive",
        "drive_unlinked":
            "✅ **اتصال Google Drive قطع شد**\n\n"
            "حساب شما از این ربات جدا شد.",

        # ── Upload flow ─────────────────────────────────────────────────────
        "upload_starting":       "⏳ **در حال شروع…**",
        "upload_hint":           "کافی است فایل را مستقیماً در این چت بفرستید!",
        "upload_already_running":
            "⏳ آپلود دیگری در حال انجام است. لطفاً صبر کنید تا تمام شود.",
        "upload_rate_limited":
            "🚫 **خیلی سریع!**\n\n"
            "فایل‌ها را خیلی سریع می‌فرستید. لطفاً **{wait} ثانیه** صبر کنید.",
        "upload_too_large":
            "❌ **فایل خیلی بزرگ است**\n\n"
            "حداکثر مجاز: **۲ گیگابایت**\n"
            "فایل شما: **{size}**",
        "download_header":  "📥 **در حال دانلود از تلگرام…**",
        "upload_header":    "📤 **در حال آپلود به Google Drive…**",
        "upload_complete":
            "✅ **آپلود کامل شد!**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📄  **فایل:** `{name}`\n"
            "📦  **حجم:** {size}\n\n"
            "🔗 **[باز کردن / دانلود]({link})**",
        "upload_failed":
            "❌ **آپلود ناموفق بود**\n\nمشکلی پیش آمد. لطفاً دوباره تلاش کنید.",

        # ── My stats ────────────────────────────────────────────────────────
        "my_stats":
            "📊 **آمار آپلودهای شما**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📤  کل آپلودها: **{total}**\n"
            "💾  داده ذخیره‌شده: **{size}**",

        # ── Admin panel ─────────────────────────────────────────────────────
        "admin_panel_title":     "⚙️ **پنل مدیریت**\nیک گزینه را انتخاب کنید:",
        "btn_admin_stats":       "📊  آمار ربات",
        "btn_admin_broadcast":   "📢  ارسال همگانی",
        "btn_bot_off":           "🔴  خاموش کردن ربات",
        "btn_bot_on":            "🟢  روشن کردن ربات",
        "btn_back_main":         "◀️  منوی اصلی",
        "btn_back_admin":        "◀️  پنل مدیریت",

        "admin_stats":
            "📊 **آمار ربات**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👥  کل کاربران: **{users}**\n"
            "📤  کل آپلودها: **{uploads}**\n"
            "💾  داده ذخیره‌شده: **{size}**",

        "broadcast_prompt":
            "📢 **ارسال همگانی**\n\n"
            "پیامی که می‌خواهید برای همه کاربران ارسال شود را بفرستید.\n"
            "متن، عکس، ویدیو، سند و صدا پشتیبانی می‌شود.",
        "broadcast_sending":  "📢 در حال ارسال همگانی…",
        "broadcast_done":
            "📢 **ارسال همگانی کامل شد**\n\n"
            "✅  موفق: **{ok}**\n"
            "❌  ناموفق: **{fail}**",

        "bot_toggled_on":   "✅ ربات اکنون آنلاین است.",
        "bot_toggled_off":  "🔴 ربات اکنون آفلاین است (حالت تعمیر).",

        "action_cancelled": "✅ عملیات لغو شد.",
    },
}


def t(key: str, lang: str = "en") -> str:
    """Return the string for *key* in *lang*, falling back to English."""
    return STRINGS.get(lang, STRINGS["en"]).get(key) or STRINGS["en"].get(key, key)
