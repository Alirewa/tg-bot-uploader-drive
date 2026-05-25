<div dir="ltr">

# 🤖 Telegram → Google Drive Uploader Bot

A production-ready Telegram bot that uploads files (up to **2 GB**) directly to each user's personal Google Drive (15 GB) and returns a shareable link — with a bilingual **English / Persian** interface.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-2.x-blue)](https://pyrogram.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## ✨ Features

| Feature | Description |
|---|---|
| **Up to 2 GB** | Pyrogram's MTProto protocol bypasses the 50 MB HTTP Bot API limit |
| **Personal Google Drive** | Each user authenticates their own 15 GB Drive via OAuth2 |
| **Bilingual UI** | Full English & Persian (Farsi) interface — user chooses on first `/start` |
| **Live Progress Bar** | Real-time download + upload progress with speed and ETA |
| **Force Join** | Users must join required channels before using the bot |
| **Rate Limiting** | Anti-spam: configurable upload quota per time window |
| **Admin Panel** | Bot statistics, broadcast to all users, bot on/off toggle |
| **Zero-Conflict Install** | Dedicated directory, venv, and systemd service name — safe alongside other bots |

---

## 🚀 Quick Start (Ubuntu 22.04)

```bash
git clone https://github.com/Alirewa/tg-bot-uploader-drive.git
cd tg-bot-uploader-drive

# First, read the Google setup guide:
cat GOOGLE_SETUP.md

# Then run the installer as root:
sudo bash install.sh
```

The installer will:
- Install Python 3, Docker, and all dependencies
- Prompt for all required credentials
- Create an isolated environment at `/opt/gdrive-uploader-bot/`
- Register and start `gdrive-uploader.service` (systemd)

---

## ⚙️ Manual Setup

```bash
git clone https://github.com/Alirewa/tg-bot-uploader-drive.git
cd tg-bot-uploader-drive

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Fill in .env with your credentials (see table below)

python main.py
```

---

## 🔑 Configuration (`.env`)

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | ✅ | From [@BotFather](https://t.me/BotFather) |
| `ADMIN_ID` | ✅ | Your Telegram numeric user ID |
| `API_ID` | ✅ | From [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | ✅ | From [my.telegram.org](https://my.telegram.org) |
| `GOOGLE_OAUTH_CLIENT_ID` | ✅ | See `GOOGLE_SETUP.md` |
| `GOOGLE_OAUTH_CLIENT_SECRET` | ✅ | See `GOOGLE_SETUP.md` |
| `GOOGLE_OAUTH_REDIRECT_URI` | ✅ | Must be `http://localhost` |
| `FORCE_JOIN_CHANNEL_1` | ❌ | e.g. `@webdw` |
| `FORCE_JOIN_CHANNEL_2` | ❌ | e.g. `@webdwCF` |
| `DATABASE_URL` | ❌ | Default: `sqlite+aiosqlite:///bot.db` |
| `RATE_LIMIT_MAX_UPLOADS` | ❌ | Default: `3` |
| `RATE_LIMIT_WINDOW_SECONDS` | ❌ | Default: `60` |

---

## 📋 Google Cloud Console Setup

See **[GOOGLE_SETUP.md](GOOGLE_SETUP.md)** for the full step-by-step guide covering:
- Creating a project and enabling the Drive API
- Configuring the OAuth consent screen
- Generating Client ID & Secret
- Setting the correct Authorized Redirect URI (`http://localhost`)

---

## 🤖 Bot Usage

1. Send `/start` → choose language (English / فارسی)
2. Tap **Authenticate Google Drive** → follow the OAuth2 steps
3. Send any file → bot downloads it and uploads to your personal Drive
4. Receive a shareable public link

---

## 🛠️ Service Management

```bash
# View logs
journalctl -u gdrive-uploader -f

# Restart
systemctl restart gdrive-uploader

# Stop
systemctl stop gdrive-uploader
```

---

## 📁 Project Structure

```
tg-bot-uploader-drive/
├── main.py
├── config.py
├── install.sh
├── GOOGLE_SETUP.md
├── database/
│   ├── models.py       # User, Upload, RateLimit, BotSetting
│   └── session.py
├── handlers/
│   ├── start.py        # /start, language selection, main menu
│   ├── admin.py        # Admin panel
│   ├── upload.py       # File upload flow
│   └── oauth.py        # Google Drive OAuth2 linking
├── services/
│   ├── drive_service.py   # Google Drive API (upload, auth)
│   ├── force_join.py
│   └── rate_limiter.py
└── utils/
    ├── strings.py      # All bilingual strings (EN + FA)
    ├── keyboards.py    # Inline keyboard builders
    ├── progress.py     # Live progress bar
    ├── helpers.py
    └── state.py
```

---

## 📄 License

MIT — see [LICENSE](LICENSE)

</div>

---
---

<div dir="rtl">

# 🤖 ربات آپلودر تلگرام به Google Drive

یک ربات تلگرام آماده برای استقرار که فایل‌ها (تا **۲ گیگابایت**) را مستقیماً در Google Drive شخصی هر کاربر (۱۵ گیگابایت) آپلود می‌کند و لینک اشتراک‌گذاری برمی‌گرداند — با رابط کاربری دوزبانه **فارسی / انگلیسی**.

---

## ✨ امکانات

| امکان | توضیح |
|---|---|
| **تا ۲ گیگابایت** | پروتکل MTProto Pyrogram محدودیت ۵۰ مگابایتی Bot API را دور می‌زند |
| **Google Drive شخصی** | هر کاربر Drive 15 گیگابایتی خود را از طریق OAuth2 متصل می‌کند |
| **رابط دوزبانه** | رابط کامل فارسی و انگلیسی — کاربر در اولین `/start` انتخاب می‌کند |
| **نوار پیشرفت زنده** | نمایش پیشرفت دانلود + آپلود با سرعت و زمان باقیمانده |
| **عضویت اجباری** | کاربران باید در کانال‌های مشخص عضو باشند |
| **محدودیت نرخ** | ضد اسپم: سهمیه آپلود قابل تنظیم در بازه زمانی |
| **پنل مدیریت** | آمار ربات، ارسال همگانی، روشن/خاموش کردن ربات |
| **نصب بدون تداخل** | دایرکتوری، venv، و نام سرویس systemd اختصاصی |

---

## 🚀 راه‌اندازی سریع (Ubuntu 22.04)

```bash
git clone https://github.com/Alirewa/tg-bot-uploader-drive.git
cd tg-bot-uploader-drive

# ابتدا راهنمای تنظیم Google را بخوانید:
cat GOOGLE_SETUP.md

# سپس اسکریپت نصب را با دسترسی root اجرا کنید:
sudo bash install.sh
```

اسکریپت نصب به طور خودکار:
- Python 3، Docker و تمام وابستگی‌ها را نصب می‌کند
- اعتبارنامه‌های لازم را می‌پرسد
- یک محیط ایزوله در `/opt/gdrive-uploader-bot/` ایجاد می‌کند
- سرویس `gdrive-uploader.service` را ثبت و اجرا می‌کند

---

## ⚙️ نصب دستی

```bash
git clone https://github.com/Alirewa/tg-bot-uploader-drive.git
cd tg-bot-uploader-drive

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# فایل .env را با اعتبارنامه‌های خود پر کنید

python main.py
```

---

## 🔑 پیکربندی (`.env`)

| متغیر | الزامی | توضیح |
|---|---|---|
| `BOT_TOKEN` | ✅ | از [@BotFather](https://t.me/BotFather) |
| `ADMIN_ID` | ✅ | آیدی عددی تلگرام شما |
| `API_ID` | ✅ | از [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | ✅ | از [my.telegram.org](https://my.telegram.org) |
| `GOOGLE_OAUTH_CLIENT_ID` | ✅ | فایل `GOOGLE_SETUP.md` را ببینید |
| `GOOGLE_OAUTH_CLIENT_SECRET` | ✅ | فایل `GOOGLE_SETUP.md` را ببینید |
| `GOOGLE_OAUTH_REDIRECT_URI` | ✅ | باید دقیقاً `http://localhost` باشد |

---

## 📋 راهنمای تنظیم Google Cloud Console

فایل **[GOOGLE_SETUP.md](GOOGLE_SETUP.md)** را ببینید — راهنمای کامل گام‌به‌گام:
- ایجاد پروژه و فعال‌سازی Drive API
- پیکربندی صفحه رضایت OAuth
- تولید Client ID و Secret
- تنظیم دقیق Authorized Redirect URI

---

## 🤖 نحوه استفاده از ربات

۱. `/start` بفرستید → زبان را انتخاب کنید
۲. روی **احراز هویت Google Drive** بزنید → مراحل OAuth2 را دنبال کنید
۳. هر فایلی بفرستید → ربات دانلود و در Drive شما آپلود می‌کند
۴. لینک قابل اشتراک‌گذاری دریافت کنید

---

## 📄 مجوز

MIT

</div>
