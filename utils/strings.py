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
            "Send me any of the following and I'll upload it to your Google Drive:\n"
            "📎 Files · 🎬 Videos · 🎵 Music · 📸 Photos\n"
            "🔗 YouTube · Instagram · Twitter/X · TikTok · Vimeo links\n\n"
            "📊 **Normal plan:** 2 GB/day · **Premium** (invite 5 friends): Unlimited",
        "channels_footer": "📢 **Our Channels:** {channels}",
        "btn_upload_info":    "📤  Send a File to Upload",
        "btn_link_drive":     "🔑  Authenticate Google Drive  ←",
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
        "btn_authenticate": "🔑  Authenticate Google Drive  ←",

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
        "oauth_instructions_auto":
            "👆 Tap the link below to connect your Google Drive:\n\n"
            "{auth_url}\n\n"
            "Sign in with your Google account and grant permission.\n\n"
            "✅ That's all — the bot will automatically detect the authorization "
            "and send you a confirmation here. You can close the browser once "
            "you see the green confirmation page.",
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
        "upload_hint":           "Send me a file, video, photo, audio, or a YouTube/Instagram/TikTok link!",
        "upload_already_running":
            "⏳ You already have an upload in progress. Please wait for it to finish.",
        "upload_rate_limited":
            "🚫 **Slow Down!**\n\n"
            "You're uploading too fast. Please wait **{wait}s** and try again.",
        "upload_cooldown":
            "⏱ **Please wait {seconds}s** before sending another upload request.",
        "upload_too_large":
            "❌ **File Too Large**\n\n"
            "Maximum allowed: **2 GB**\n"
            "Your file: **{size}**",
        "download_header":     "📥 **Downloading from Telegram…**",
        "download_header_url": "{icon} **Downloading from {platform}…**",
        "upload_header":       "📤 **Uploading to Google Drive…**",

        # ── YouTube quality selection ────────────────────────────────────────
        "yt_quality_prompt":
            "🎬 **YouTube link detected!**\n\n"
            "Choose the download quality:",
        "btn_ytq_best":  "📹  Video — Best Quality",
        "btn_ytq_720":   "📹  Video — 720p",
        "btn_ytq_480":   "📹  Video — 480p",
        "btn_ytq_audio": "🎵  Audio Only (MP3)",

        # ── Destination selection ────────────────────────────────────────────
        "dest_select_prompt":
            "{icon} **{platform}** link detected!\n\n"
            "Where do you want this file?",
        "btn_dest_telegram": "📱  Send to Telegram  (auto-delete 2 min)",
        "btn_dest_drive":    "📁  Upload to Google Drive",
        "tg_sending":        "📤 **Sending to Telegram…**",
        "tg_delivery_caption":
            "📎 `{name}`\n💾 {size}",
        "tg_delivery_warning":
            "⚠️ **This file will be auto-deleted in 2 minutes!**\n\n"
            "Forward this message now to keep a permanent copy.\n"
            "The file disappears from this chat in **2 min**.",
        "tg_delivery_deleted": "🗑 File auto-deleted from this chat.",

        # ── URL download ────────────────────────────────────────────────────
        "url_processing":
            "{icon} **{platform}** link detected — downloading…",
        "url_unsupported":
            "❌ **Unsupported Link**\n\n"
            "Supported platforms:\n"
            "🎬 YouTube · 📸 Instagram · 🐦 Twitter/X\n"
            "🎵 TikTok · 🎥 Vimeo · 🎵 SoundCloud · 🎬 Dailymotion\n"
            "📦 MediaFire · Dropbox · WeTransfer · 🔗 Direct links",
        "url_download_failed":
            "❌ **Download Failed**\n\n"
            "The link may be private, region-locked, or no longer available.\n"
            "Please check the link and try again.",

        # ── Unsupported message ──────────────────────────────────────────────
        "unsupported_message":
            "❌ **I can't process this.**\n\n"
            "Here's what I support:\n"
            "📎 Files · 🎬 Videos · 🎵 Music · 📸 Photos\n"
            "🔗 YouTube · Instagram · Twitter/X · TikTok · Vimeo\n"
            "🔄 Public Google Drive links\n\n"
            "Please send one of the above.",

        # ── Drive → Telegram ────────────────────────────────────────────────
        "premium_required_drive":
            "⭐ **Premium Feature**\n\n"
            "Converting Google Drive links to Telegram files is available for **Premium** users only.\n\n"
            "🔓 **Get Premium free:** invite **5 friends** via your referral link.\n"
            "They just need to start the bot — that's it.",
        "drive_link_use_button":
            "📥 To convert a Google Drive link to a Telegram file, "
            "tap the **Convert Google Drive Link** button in the menu first.",
        "drive_to_tg_error":
            "❌ **Download Failed**\n\n"
            "`{error}`\n\n"
            "Make sure the file is shared with **Anyone with the link** and try again.",
        "btn_drive_to_tg":       "📥  Convert Google Drive Link → Telegram",
        "drive_to_tg_prompt":
            "📎 Send a **Google Drive link** and I'll send the file back to you here.\n\n"
            "⚠️ The file must be shared with **Anyone with the link** (public access).",
        "drive_to_tg_downloading": "⬇️ **Downloading from Google Drive…**",
        "drive_to_tg_sending":     "📤 **Sending to Telegram…**",
        "drive_to_tg_not_public":
            "❌ **File Not Accessible**\n\n"
            "Make sure the file is shared with **Anyone with the link** in Google Drive.",
        "drive_to_tg_invalid":
            "❌ That doesn't look like a Google Drive link.\n\n"
            "Please send a link like:\n`https://drive.google.com/file/d/FILE_ID/view`",

        # ── Admin user list ──────────────────────────────────────────────────
        "btn_search_user":         "🔍  Search by ID",
        "admin_users_header":      "👥 **Users** — page {page}/{pages} · total: {total}",

        # ── Drive storage ────────────────────────────────────────────────────
        "btn_drive_storage":  "☁️  Storage Usage",
        "btn_open_drive":     "🌐  Open Google Drive",
        "drive_storage_checking": "🔄 Checking your Drive storage…",
        "drive_storage_info":
            "☁️ **Google Drive Storage**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📦 Used: **{usage}** of **{limit}**\n"
            "📊 [{bar}] {pct:.1f}%\n\n"
            "To free up space, open Google Drive and delete files you no longer need.",
        "drive_storage_error":
            "❌ Could not retrieve storage info.\n`{error}`",
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

        # ── Drive selection ──────────────────────────────────────────────────
        "drive_select_prompt":
            "📂 **Choose Storage**\n\n"
            "Where would you like to upload this file?",
        "btn_use_my_drive":        "📁  My Google Drive (personal)",
        "btn_authenticate_upload": "🔗  Link My Drive & Upload",
        "btn_use_bot_drive":       "🤖  Bot's Drive (free, 48h)",
        "btn_bot_drive_full":      "🔴  Bot Drive Full — wait 48h",
        "btn_cancel":              "❌  Cancel",
        "upload_cancelled":        "✅ Upload cancelled.",

        "bot_drive_full":
            "🔴 **Bot Drive Is Full**\n\n"
            "The bot's shared Google Drive storage is currently at capacity.\n\n"
            "Files are automatically deleted every **48 hours**, so please try again later.\n\n"
            "You can also link your own Google Drive (free 15 GB) by tapping the button below.",
        "upload_header_bot":  "📤 **Uploading to Bot Drive…**",

        "daily_limit_count":
            "🚫 **Daily Upload Limit Reached**\n\n"
            "You can upload a maximum of **5 files per day**.\n\n"
            "🔓 **Remove this limit forever:** invite **3 friends** using your referral link.\n"
            "They just need to start the bot — that's it.",
        "daily_limit_size":
            "🚫 **Daily Upload Quota Reached**\n\n"
            "Your plan allows **2 GB per day**.\n\n"
            "🔓 **Upgrade to Premium (unlimited):** invite **5 friends** using your referral link.\n"
            "They just need to start the bot — that's it.",

        "btn_referral": "🔗  Referral Link",
        "referral_info":
            "🔗 **Your Referral Link**\n\n"
            "`{link}`\n\n"
            "Share this link with friends. When **5 friends** start the bot through your link, "
            "your daily upload limit is **permanently removed** (Premium).\n\n"
            "📊 Referrals so far: **{count}/{needed}** {status}",
        "referral_unlocked_badge": "✅ Limit removed!",
        "referral_pending_badge": "⏳ Keep going!",
        "referral_welcome":
            "👋 You were invited by a friend!\n\n"
            "Your friend gets closer to removing their upload limit.",

        "drive_status_checking": "🔄 Checking connection…",
        "drive_status_ok":
            "✅ **Google Drive — Connected**\n\n"
            "Your account is active and the connection is working correctly.",
        "drive_status_error":
            "❌ **Google Drive — Connection Error**\n\n"
            "Could not reach your Google Drive. This may happen if you revoked access "
            "or the token expired.\n\n"
            "**Error:** `{error}`\n\n"
            "Tap **Re-authenticate** to reconnect.",
        "btn_check_drive_status": "🔄  Check Connection Status",

        # ── Delete Drive data ────────────────────────────────────────────────
        "btn_delete_drive_data":  "🗑  Delete All My Drive Data",
        "btn_confirm_delete_yes": "⚠️  Yes, delete everything",
        "btn_confirm_delete_no":  "❌  Cancel",
        "delete_drive_data_prompt":
            "⚠️ **Delete All Drive Data?**\n\n"
            "This will:\n"
            "• 🗑 Delete all files the bot uploaded to your Google Drive\n"
            "• 🔓 Unlink your Google Drive account\n"
            "• 📋 Clear your upload history\n\n"
            "**This action cannot be undone.**\nAre you sure?",
        "delete_drive_data_done":
            "✅ **All Drive data deleted.**\n\n"
            "Your Google Drive has been unlinked and all uploaded files have been removed.",
        "delete_drive_data_partial":
            "✅ **Drive unlinked.**\n\n"
            "Account disconnected. {deleted} file(s) deleted, {failed} could not be removed "
            "(may already be gone from Drive).",

        # ── Reply keyboard labels ────────────────────────────────────────────
        "rbtn_upload":   "📤  Upload",
        "rbtn_my_drive": "🔑  My Drive",
        "rbtn_stats":    "📊  Stats",
        "rbtn_referral": "🔗  Referral",
        "reply_kb_hint": "Use the menu below for quick access:",

        "btn_support": "💎  Support Project",
        "support_text":
            "💎 **Support This Project**\n\n"
            "This bot is fully **open-source** and free to use.\n\n"
            "If you find it useful, please consider giving it a ⭐ on GitHub — "
            "it helps the project grow and motivates adding more features.\n\n"
            "🔗 **[Star on GitHub]({github_url})**",

        "btn_admin_users":    "👥  User Management",
        "btn_admin_channels": "📢  Channel Management",
        "btn_admin_auto_msg": "📨  Auto Message Link",

        # ── Auto message ─────────────────────────────────────────────────────
        "admin_auto_msg_status_none":
            "📨 **Auto Message Link**\n\n"
            "No auto message is set.\n\n"
            "Send me any message (text, photo, video, file, audio…) and I'll "
            "generate a `/start` link. Anyone who taps that link will receive your message automatically.",
        "admin_auto_msg_status_set":
            "📨 **Auto Message Link**\n\n"
            "✅ An auto message is currently set.\n\n"
            "🔗 **Share this link:**\n`{link}`\n\n"
            "Anyone who taps it will receive the saved message.\n\n"
            "Send a new message to replace it, or tap **Clear** to remove it.",
        "admin_auto_msg_prompt":
            "📨 **Set Auto Message**\n\n"
            "Send me the message you want users to receive when they tap the link.\n"
            "Supported: text, photo, video, file, audio, voice, animation.",
        "admin_auto_msg_saved":
            "✅ **Auto message saved!**\n\n"
            "🔗 **Share this link:**\n`{link}`\n\n"
            "Every user who taps it will receive your message automatically.",
        "admin_auto_msg_cleared": "✅ Auto message cleared.",
        "btn_auto_msg_set":   "📨  Set / Replace Message",
        "btn_auto_msg_clear": "🗑  Clear Auto Message",

        "admin_ask_user_id": "👤 Send the user's **Telegram ID** (numeric):",
        "admin_user_not_found": "❌ User not found in database.",
        "admin_user_info":
            "👤 **User Info**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🆔 ID: `{id}`\n"
            "👤 Name: {name}\n"
            "📛 Username: @{username}\n"
            "🌐 Language: {lang}\n"
            "📅 Joined: {joined}\n"
            "🔗 Drive: {drive}\n"
            "👑 Admin: {is_admin}\n"
            "🔓 Limit exempt: {exempt}\n"
            "🎯 Referrals: {refs}\n"
            "📤 Uploads today: {daily_count} ({daily_size})",
        "btn_make_admin": "👑  Make Admin",
        "btn_remove_admin": "👤  Remove Admin",
        "btn_grant_exempt": "🔓  Remove Upload Limit",
        "btn_revoke_exempt": "🔒  Restore Upload Limit",
        "admin_action_done": "✅ Done.",

        "channels_menu_title":
            "📢 **Force-Join Channels**\nChannels users must join before using the bot:",
        "channels_empty": "(none)",
        "btn_add_channel": "➕  Add Channel",
        "btn_remove_channel": "🗑  Remove",
        "admin_ask_channel": "📢 Send the channel username (e.g. @mychannel):",
        "admin_channel_invalid": "❌ Invalid. Send the channel username starting with @",
        "admin_channel_added": "✅ Channel added.",
        "admin_channel_removed": "✅ Channel removed.",
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
            "هر کدام از موارد زیر را بفرستید تا در Google Drive آپلود کنم:\n"
            "📎 فایل · 🎬 ویدیو · 🎵 موزیک · 📸 عکس\n"
            "🔗 لینک YouTube · Instagram · Twitter/X · TikTok · Vimeo\n\n"
            "📊 **پلن عادی:** ۲ گیگابایت در روز · **پریمیوم** (دعوت ۵ دوست): نامحدود",
        "channels_footer": "📢 **کانال‌های ما:** {channels}",
        "btn_upload_info":    "📤  ارسال فایل برای آپلود",
        "btn_link_drive":     "🔑  احراز هویت Google Drive  ←",
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
        "btn_authenticate": "🔑  احراز هویت Google Drive  ←",

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
        "oauth_instructions_auto":
            "👆 روی لینک زیر بزنید تا Google Drive خود را متصل کنید:\n\n"
            "{auth_url}\n\n"
            "با حساب Google وارد شوید و مجوز دسترسی بدهید.\n\n"
            "✅ همین — ربات به‌صورت خودکار تأیید را دریافت می‌کند و پیام موفقیت "
            "برایتان می‌فرستد. پس از دیدن صفحه سبز، مرورگر را ببندید.",
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
        "upload_hint":           "فایل، ویدیو، عکس، موزیک یا لینک YouTube/Instagram/TikTok بفرستید!",
        "upload_already_running":
            "⏳ آپلود دیگری در حال انجام است. لطفاً صبر کنید تا تمام شود.",
        "upload_rate_limited":
            "🚫 **خیلی سریع!**\n\n"
            "فایل‌ها را خیلی سریع می‌فرستید. لطفاً **{wait} ثانیه** صبر کنید.",
        "upload_cooldown":
            "⏱ لطفاً **{seconds} ثانیه** صبر کنید سپس مجدداً ارسال کنید.",
        "upload_too_large":
            "❌ **فایل خیلی بزرگ است**\n\n"
            "حداکثر مجاز: **۲ گیگابایت**\n"
            "فایل شما: **{size}**",
        "download_header":     "📥 **در حال دانلود از تلگرام…**",
        "download_header_url": "{icon} **در حال دانلود از {platform}…**",
        "upload_header":       "📤 **در حال آپلود به Google Drive…**",

        # ── YouTube quality selection ────────────────────────────────────────
        "yt_quality_prompt":
            "🎬 **لینک YouTube شناسایی شد!**\n\n"
            "کیفیت دانلود را انتخاب کنید:",
        "btn_ytq_best":  "📹  ویدیو — بهترین کیفیت",
        "btn_ytq_720":   "📹  ویدیو — 720p",
        "btn_ytq_480":   "📹  ویدیو — 480p",
        "btn_ytq_audio": "🎵  فقط صدا (MP3)",

        # ── Destination selection ────────────────────────────────────────────
        "dest_select_prompt":
            "{icon} لینک **{platform}** شناسایی شد!\n\n"
            "فایل رو کجا بخوای؟",
        "btn_dest_telegram": "📱  ارسال به تلگرام  (حذف خودکار ۲ دقیقه)",
        "btn_dest_drive":    "📁  آپلود به Google Drive",
        "tg_sending":        "📤 **در حال ارسال به تلگرام…**",
        "tg_delivery_caption":
            "📎 `{name}`\n💾 {size}",
        "tg_delivery_warning":
            "⚠️ **این فایل ۲ دقیقه دیگه حذف میشه!**\n\n"
            "همین الان پیام رو فوروارد کن تا ذخیره بمونه.\n"
            "فایل **۲ دقیقه دیگه** از این چت پاک میشه.",
        "tg_delivery_deleted": "🗑 فایل از این چت حذف شد.",

        # ── URL download ────────────────────────────────────────────────────
        "url_processing":
            "{icon} لینک **{platform}** شناسایی شد — در حال دانلود…",
        "url_unsupported":
            "❌ **لینک پشتیبانی نمی‌شود**\n\n"
            "پلتفرم‌های پشتیبانی‌شده:\n"
            "🎬 YouTube · 📸 Instagram · 🐦 Twitter/X\n"
            "🎵 TikTok · 🎥 Vimeo · 🎵 SoundCloud · 🎬 Dailymotion\n"
            "📦 MediaFire · Dropbox · WeTransfer · 🔗 لینک مستقیم",
        "url_download_failed":
            "❌ **دانلود ناموفق بود**\n\n"
            "لینک ممکن است خصوصی، منطقه‌بندی‌شده یا حذف‌شده باشد.\n"
            "لینک را بررسی کرده و دوباره تلاش کنید.",

        # ── Unsupported message ──────────────────────────────────────────────
        "unsupported_message":
            "❌ **این محتوا پشتیبانی نمی‌شود.**\n\n"
            "موارد پشتیبانی‌شده:\n"
            "📎 فایل · 🎬 ویدیو · 🎵 موزیک · 📸 عکس\n"
            "🔗 YouTube · Instagram · Twitter/X · TikTok · Vimeo\n"
            "🔄 لینک عمومی Google Drive\n\n"
            "لطفاً یکی از موارد بالا را بفرستید.",

        # ── Drive → Telegram ────────────────────────────────────────────────
        "premium_required_drive":
            "⭐ **قابلیت پریمیوم**\n\n"
            "تبدیل لینک گوگل درایو به فایل تلگرام فقط برای کاربران **پریمیوم** در دسترس است.\n\n"
            "🔓 **پریمیوم رایگان:** با لینک رفرال خود **۵ دوست** دعوت کنید.\n"
            "کافی است آن‌ها ربات را استارت بزنند — همین.",
        "drive_link_use_button":
            "📥 برای تبدیل لینک گوگل درایو به فایل تلگرام، "
            "ابتدا روی دکمه **تبدیل لینک گوگل درایو** در منو بزنید.",
        "drive_to_tg_error":
            "❌ **دانلود ناموفق بود**\n\n"
            "`{error}`\n\n"
            "مطمئن شوید فایل با **هر کسی که لینک دارد** به اشتراک گذاشته شده و دوباره تلاش کنید.",
        "btn_drive_to_tg":       "📥  تبدیل لینک گوگل درایو به فایل تلگرام",
        "drive_to_tg_prompt":
            "📎 یک **لینک Google Drive** بفرستید تا فایل را اینجا برایتان بفرستم.\n\n"
            "⚠️ فایل باید با **هر کسی که لینک دارد** (دسترسی عمومی) به اشتراک گذاشته شده باشد.",
        "drive_to_tg_downloading": "⬇️ **در حال دانلود از Google Drive…**",
        "drive_to_tg_sending":     "📤 **در حال ارسال به تلگرام…**",
        "drive_to_tg_not_public":
            "❌ **فایل قابل دسترسی نیست**\n\n"
            "مطمئن شوید فایل در Google Drive با **هر کسی که لینک دارد** به اشتراک گذاشته شده.",
        "drive_to_tg_invalid":
            "❌ این لینک Google Drive معتبر نیست.\n\n"
            "لطفاً لینکی مثل این بفرستید:\n`https://drive.google.com/file/d/FILE_ID/view`",

        # ── Admin user list ──────────────────────────────────────────────────
        "btn_search_user":     "🔍  جستجو با شناسه",
        "admin_users_header":  "👥 **کاربران** — صفحه {page}/{pages} · کل: {total}",

        # ── Drive storage ────────────────────────────────────────────────────
        "btn_drive_storage":  "☁️  میزان فضای مصرفی",
        "btn_open_drive":     "🌐  باز کردن Google Drive",
        "drive_storage_checking": "🔄 در حال بررسی فضای Drive شما…",
        "drive_storage_info":
            "☁️ **فضای Google Drive**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📦 مصرف‌شده: **{usage}** از **{limit}**\n"
            "📊 [{bar}] {pct:.1f}%\n\n"
            "برای آزادسازی فضا، Google Drive را باز کنید و فایل‌های اضافه را حذف کنید.",
        "drive_storage_error":
            "❌ دریافت اطلاعات فضا ناموفق بود.\n`{error}`",
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

        # ── Drive selection ──────────────────────────────────────────────────
        "drive_select_prompt":
            "📂 **انتخاب فضای ذخیره‌سازی**\n\n"
            "فایل را کجا آپلود کنم؟",
        "btn_use_my_drive":        "📁  Google Drive من (شخصی)",
        "btn_authenticate_upload": "🔗  اتصال Drive من و آپلود",
        "btn_use_bot_drive":       "🤖  فضای ربات (رایگان، ۴۸ ساعت)",
        "btn_bot_drive_full":      "🔴  فضای ربات پر است — ۴۸ ساعت صبر کنید",
        "btn_cancel":              "❌  لغو",
        "upload_cancelled":        "✅ آپلود لغو شد.",

        "bot_drive_full":
            "🔴 **فضای ربات پر است**\n\n"
            "فضای اشتراکی Google Drive ربات در حال حاضر پر است.\n\n"
            "هر **۴۸ ساعت** فایل‌ها به‌طور خودکار حذف می‌شوند. لطفاً بعداً تلاش کنید.\n\n"
            "همچنین می‌توانید Google Drive شخصی خود (۱۵ گیگابایت رایگان) را متصل کنید.",
        "upload_header_bot":  "📤 **در حال آپلود به فضای ربات…**",

        "daily_limit_count":
            "🚫 **محدودیت روزانه آپلود**\n\n"
            "شما می‌توانید حداکثر **۵ فایل در روز** آپلود کنید.\n\n"
            "🔓 **حذف دائمی این محدودیت:** با لینک رفرال خود **۳ دوست** دعوت کنید.\n"
            "کافی است آن‌ها ربات را استارت بزنند — همین.",
        "daily_limit_size":
            "🚫 **سهمیه روزانه آپلود تمام شد**\n\n"
            "پلن شما امکان **۲ گیگابایت در روز** را دارد.\n\n"
            "🔓 **ارتقا به پریمیوم (نامحدود):** با لینک رفرال خود **۵ دوست** دعوت کنید.\n"
            "کافی است آن‌ها ربات را استارت بزنند — همین.",

        "btn_referral": "🔗  لینک رفرال",
        "referral_info":
            "🔗 **لینک رفرال شما**\n\n"
            "`{link}`\n\n"
            "این لینک را با دوستانتان به اشتراک بگذارید. وقتی **۵ دوست** از طریق لینک شما ربات را استارت بزنند، "
            "محدودیت روزانه آپلود شما **برای همیشه** حذف می‌شود (پریمیوم).\n\n"
            "📊 رفرال‌ها تا کنون: **{count}/{needed}** {status}",
        "referral_unlocked_badge": "✅ محدودیت حذف شد!",
        "referral_pending_badge": "⏳ ادامه دهید!",
        "referral_welcome":
            "👋 شما توسط یک دوست دعوت شدید!\n\n"
            "دوستتان به حذف محدودیت آپلود خود نزدیک‌تر شد.",

        "drive_status_checking": "🔄 در حال بررسی اتصال…",
        "drive_status_ok":
            "✅ **Google Drive — متصل**\n\n"
            "حساب شما فعال است و اتصال به درستی کار می‌کند.",
        "drive_status_error":
            "❌ **Google Drive — خطای اتصال**\n\n"
            "نمی‌توان به Google Drive شما دسترسی داشت. این ممکن است به دلیل لغو دسترسی "
            "یا انقضای توکن باشد.\n\n"
            "**خطا:** `{error}`\n\n"
            "روی **احراز هویت مجدد** ضربه بزنید تا دوباره متصل شوید.",
        "btn_check_drive_status": "🔄  بررسی وضعیت اتصال",

        # ── حذف داده درایو ───────────────────────────────────────────────────
        "btn_delete_drive_data":  "🗑  حذف تمام اطلاعات درایو",
        "btn_confirm_delete_yes": "⚠️  بله، همه چیز رو حذف کن",
        "btn_confirm_delete_no":  "❌  لغو",
        "delete_drive_data_prompt":
            "⚠️ **حذف تمام اطلاعات درایو؟**\n\n"
            "این عمل انجام می‌شه:\n"
            "• 🗑 حذف همه فایل‌هایی که ربات در Google Drive آپلود کرده\n"
            "• 🔓 قطع اتصال حساب Google Drive\n"
            "• 📋 پاک کردن تاریخچه آپلودها\n\n"
            "**این عمل قابل بازگشت نیست.**\nمطمئنی؟",
        "delete_drive_data_done":
            "✅ **تمام اطلاعات درایو حذف شد.**\n\n"
            "Google Drive شما قطع شد و تمام فایل‌های آپلودشده حذف شدند.",
        "delete_drive_data_partial":
            "✅ **درایو قطع شد.**\n\n"
            "{deleted} فایل حذف شد، {failed} فایل حذف نشد "
            "(احتمالاً از قبل از درایو حذف شده بودند).",

        # ── دکمه‌های کیبورد پایین ────────────────────────────────────────────
        "rbtn_upload":   "📤  آپلود",
        "rbtn_my_drive": "🔑  درایو من",
        "rbtn_stats":    "📊  آمار",
        "rbtn_referral": "🔗  رفرال",
        "reply_kb_hint": "از منوی پایین برای دسترسی سریع استفاده کنید:",

        "btn_support": "💎  حمایت از پروژه",
        "support_text":
            "💎 **حمایت از این پروژه**\n\n"
            "این ربات کاملاً **متن‌باز** و رایگان است.\n\n"
            "اگر برایتان مفید بوده، لطفاً در GitHub ستاره ⭐ بدهید — "
            "این کمک می‌کند پروژه رشد کند و امکانات بیشتری اضافه شود.\n\n"
            "🔗 **[ستاره دادن در GitHub]({github_url})**",

        "btn_admin_users":    "👥  مدیریت کاربران",
        "btn_admin_channels": "📢  مدیریت کانال‌ها",
        "btn_admin_auto_msg": "📨  لینک پیام خودکار",

        # ── Auto message ─────────────────────────────────────────────────────
        "admin_auto_msg_status_none":
            "📨 **لینک پیام خودکار**\n\n"
            "هیچ پیامی ست نشده است.\n\n"
            "هر پیامی بفرستید (متن، عکس، ویدیو، فایل، صدا…) یک لینک `/start` برایتان می‌سازم. "
            "هر کسی آن لینک را بزند، پیام شما را دریافت می‌کند.",
        "admin_auto_msg_status_set":
            "📨 **لینک پیام خودکار**\n\n"
            "✅ یک پیام خودکار ست شده است.\n\n"
            "🔗 **لینک را به اشتراک بگذارید:**\n`{link}`\n\n"
            "هر کسی روی لینک بزند پیام ذخیره‌شده را دریافت می‌کند.\n\n"
            "برای جایگزینی پیام جدیدی بفرستید، یا روی **پاک کردن** بزنید.",
        "admin_auto_msg_prompt":
            "📨 **تنظیم پیام خودکار**\n\n"
            "پیامی که می‌خواهید کاربران دریافت کنند را بفرستید.\n"
            "پشتیبانی: متن، عکس، ویدیو، فایل، صدا، ویس، انیمیشن.",
        "admin_auto_msg_saved":
            "✅ **پیام خودکار ذخیره شد!**\n\n"
            "🔗 **لینک را به اشتراک بگذارید:**\n`{link}`\n\n"
            "هر کاربری که این لینک را بزند، پیام شما را دریافت می‌کند.",
        "admin_auto_msg_cleared": "✅ پیام خودکار پاک شد.",
        "btn_auto_msg_set":   "📨  ست / جایگزینی پیام",
        "btn_auto_msg_clear": "🗑  پاک کردن پیام خودکار",

        "admin_ask_user_id": "👤 شناسه تلگرام کاربر را ارسال کنید (عدد):",
        "admin_user_not_found": "❌ کاربر در پایگاه داده یافت نشد.",
        "admin_user_info":
            "👤 **اطلاعات کاربر**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🆔 شناسه: `{id}`\n"
            "👤 نام: {name}\n"
            "📛 یوزرنیم: @{username}\n"
            "🌐 زبان: {lang}\n"
            "📅 تاریخ عضویت: {joined}\n"
            "🔗 درایو: {drive}\n"
            "👑 ادمین: {is_admin}\n"
            "🔓 معافیت محدودیت: {exempt}\n"
            "🎯 رفرال‌ها: {refs}\n"
            "📤 آپلودهای امروز: {daily_count} ({daily_size})",
        "btn_make_admin": "👑  تعیین به عنوان ادمین",
        "btn_remove_admin": "👤  حذف از ادمین",
        "btn_grant_exempt": "🔓  حذف محدودیت آپلود",
        "btn_revoke_exempt": "🔒  بازگرداندن محدودیت آپلود",
        "admin_action_done": "✅ انجام شد.",

        "channels_menu_title":
            "📢 **کانال‌های اجباری**\nکانال‌هایی که کاربران باید قبل از استفاده عضو شوند:",
        "channels_empty": "(هیچ کانالی ثبت نشده)",
        "btn_add_channel": "➕  افزودن کانال",
        "btn_remove_channel": "🗑  حذف",
        "admin_ask_channel": "📢 یوزرنیم کانال را بفرستید (مثال: @mychannel):",
        "admin_channel_invalid": "❌ نامعتبر. یوزرنیم کانال باید با @ شروع شود.",
        "admin_channel_added": "✅ کانال اضافه شد.",
        "admin_channel_removed": "✅ کانال حذف شد.",
    },
}


def t(key: str, lang: str = "en") -> str:
    """Return the string for *key* in *lang*, falling back to English."""
    return STRINGS.get(lang, STRINGS["en"]).get(key) or STRINGS["en"].get(key, key)
