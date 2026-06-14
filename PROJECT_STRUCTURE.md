# Telegram → Google Drive Uploader Bot

## هدف پروژه

ربات تلگرامی که به کاربران اجازه می‌دهد:

- **فایل‌های تلگرام** (ویدیو، عکس، صدا، سند و ...) را مستقیم به Google Drive آپلود کنند
- **لینک‌های ویدیویی** از YouTube، Instagram، TikTok، Twitter/X، Vimeo، SoundCloud، Dailymotion را دانلود و به Drive آپلود کنند
- **لینک‌های Google Drive** را بین درایوها کپی کنند

هر کاربر با OAuth2 به **درایو شخصی خودش** متصل می‌شود. علاوه بر این، ادمین می‌تواند یک **Bot Drive** مشترک (با Service Account) تعریف کند که کاربران بتوانند فایل‌هایشان را آنجا هم ذخیره کنند.

---

## استک فنی

| لایه | ابزار |
|------|-------|
| زبان | Python 3.11+ |
| ارتباط با تلگرام | Pyrogram (MTProto — تا ۴ گیگابایت) |
| دانلود ویدیو | yt-dlp + cobalt.tools fallback |
| Google Drive | google-api-python-client (OAuth2 + Service Account) |
| دیتابیس | SQLite با SQLAlchemy (async) |
| وب‌سرور OAuth | aiohttp |
| زمانبند | APScheduler |

---

## ساختار پوشه‌ها و فایل‌ها

```
.
├── main.py                    # نقطه ورود — راه‌اندازی Pyrogram، ثبت هندلرها، OAuth server
├── config.py                  # تمام متغیرهای محیطی (.env) در یک جا
├── requirements.txt           # وابستگی‌های Python
├── install.sh                 # اسکریپت نصب خودکار روی VPS
├── .env.example               # نمونه فایل محیطی
├── .gitignore
├── README.md                  # راهنمای نصب و استفاده
├── GOOGLE_SETUP.md            # راهنمای گام‌به‌گام تنظیم Google OAuth
│
├── database/                  # لایه دیتابیس
│   ├── models.py              # مدل‌های SQLAlchemy: User, Upload, Setting
│   ├── session.py             # init_db و AsyncSessionLocal
│   └── __init__.py
│
├── handlers/                  # هندلرهای تلگرام (ورودی‌های کاربر)
│   ├── admin.py               # دستورات ادمین: آمار، broadcast، تنظیمات سیستم
│   ├── middleware.py          # میان‌افزار rate-limit و ضد اسپم دکمه
│   ├── oauth.py               # جریان احراز هویت Google OAuth2 (مرحله ۱ و ۲)
│   ├── start.py               # /start، منوی اصلی، زبان، رفرال
│   ├── upload.py              # هسته اصلی: دریافت فایل/لینک → دانلود → آپلود به Drive
│   └── __init__.py            # register_all() — ثبت تمام هندلرها
│
├── services/                  # منطق تجاری (بدون وابستگی به تلگرام)
│   ├── drive_service.py       # ساخت Google Drive service، آپلود، کپی فایل
│   ├── downloader.py          # دانلود URL با yt-dlp + cobalt.tools fallback
│   ├── force_join.py          # بررسی عضویت اجباری کاربر در کانال‌ها
│   ├── oauth_server.py        # وب‌سرور aiohttp برای دریافت خودکار OAuth callback
│   ├── rate_limiter.py        # محدودیت تعداد آپلود در بازه زمانی
│   ├── scheduler.py           # پاکسازی خودکار فایل‌های قدیمی Bot Drive
│   └── __init__.py
│
├── utils/                     # ابزارهای کمکی
│   ├── bot_info.py            # نگه‌داری username ربات در حافظه
│   ├── helpers.py             # توابع DB: get_or_create_user، check_daily_limit، ...
│   ├── keyboards.py           # ساخت کیبوردهای inline تلگرام
│   ├── progress.py            # نوار پیشرفت آپلود/دانلود
│   ├── state.py               # State مشترک در حافظه: user_states، upload_cooldowns
│   ├── strings.py             # سیستم چندزبانه (FA/EN) با تابع t()
│   └── __init__.py
│
└── temp/                      # پوشه موقت (auto-created، در .gitignore)
                               # فایل‌ها بعد از آپلود یا هنگام restart پاک می‌شوند
```

---

## جریان اصلی (Upload Flow)

```
کاربر ارسال فایل / لینک
        ↓
Force-Join بررسی عضویت کانال‌ها
        ↓
Rate Limit + Cooldown بررسی
        ↓
   ┌────────────┬─────────────────┐
فایل تلگرام   لینک URL       لینک Drive
   ↓           ↓                ↓
دانلود      yt-dlp /          Google Drive
از تلگرام   cobalt.tools      Files.copy()
   └────────────┴─────────────────┘
                ↓
     انتخاب مقصد (My Drive / Bot Drive)
                ↓
      آپلود به Google Drive (resumable upload)
                ↓
       ارسال لینک فایل به کاربر
                ↓
          حذف فایل temp
```

---

## متغیرهای محیطی مهم (`.env`)

| متغیر | توضیح |
|-------|-------|
| `BOT_TOKEN` | توکن ربات از BotFather |
| `ADMIN_ID` | آیدی عددی ادمین |
| `API_ID` / `API_HASH` | از my.telegram.org |
| `GOOGLE_OAUTH_CLIENT_ID/SECRET` | از Google Cloud Console |
| `GOOGLE_OAUTH_REDIRECT_URI` | آدرس callback OAuth |
| `BOT_DRIVE_SA_JSON` | مسیر فایل Service Account (اختیاری) |
| `BOT_DRIVE_FOLDER_ID` | شناسه پوشه Bot Drive در Google Drive |
| `YTDLP_COOKIES_FILE` | مسیر cookies.txt برای دور زدن محدودیت YouTube |
| `DATABASE_URL` | آدرس دیتابیس (پیش‌فرض: SQLite) |
| `RATE_LIMIT_MAX_UPLOADS` | حداکثر آپلود در بازه زمانی |
| `MAX_FILE_SIZE_BYTES` | حداکثر سایز فایل (پیش‌فرض: ۲ گیگابایت) |
| `CLEANUP_AFTER_HOURS` | پاکسازی Bot Drive پس از چند ساعت |
