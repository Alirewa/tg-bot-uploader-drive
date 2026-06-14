<div align="center">

# ☁️ Telegram → Google Drive Uploader Bot

> A production-ready Telegram bot that uploads files up to **2 GB** directly to users' personal Google Drive and returns a shareable link — with a bilingual English / Persian interface.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-2.x-2CA5E0?style=for-the-badge)](https://pyrogram.org)
[![Google Drive](https://img.shields.io/badge/Google_Drive_API-v3-4285F4?style=for-the-badge&logo=google-drive&logoColor=white)](https://developers.google.com/drive)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

### 🤖 Live Demo

[![Demo Bot](https://img.shields.io/badge/Telegram_Bot-@webdwdu__bot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/webdwdu_bot)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Configuration](#-configuration)
- [License](#-license)

---

## 📖 Overview

**Telegram → Google Drive Uploader** is a self-hosted Telegram bot that bridges Telegram file sharing with Google Drive storage. Users send any file to the bot — documents, photos, videos, archives — and receive a shareable Google Drive link in return. Files up to **2 GB** are supported thanks to Pyrogram's MTProto protocol, bypassing the 50 MB Bot API limit.

---

## ✨ Features

- ✅ Supports files up to **2 GB** via MTProto (Pyrogram)
- ✅ Uploads directly to users' **personal** Google Drive
- ✅ Returns an instant shareable Drive link
- ✅ Bilingual interface — **English & Persian (Farsi)**
- ✅ Supports documents, photos, videos, audio, and archives
- ✅ Per-user Google Drive OAuth authentication
- ✅ Production-ready — deployable with systemd or Docker

---

## 🛠️ Tech Stack

| Technology | Role |
|---|---|
| Python 3.12 | Core bot logic |
| Pyrogram 2.x | MTProto Telegram client (bypasses 50 MB limit) |
| Google Drive API v3 | File upload & shareable link generation |
| OAuth 2.0 | Per-user Google authentication |
| SQLite | User session & token storage |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A Telegram API ID & Hash from [my.telegram.org](https://my.telegram.org)
- Google Cloud project with Drive API enabled
- OAuth 2.0 credentials (`credentials.json`)

### Installation

```bash
git clone https://github.com/Alirewa/tg-bot-uploader-drive.git
cd tg-bot-uploader-drive
pip install -r requirements.txt
cp .env.example .env
# Fill in your credentials in .env
python main.py
```

---

## ⚙️ Configuration

Edit the `.env` file with your credentials:

```env
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
BOT_TOKEN=your_bot_token
```

Place your `credentials.json` (Google OAuth) in the project root.

---

## 📄 License

Distributed under the **MIT License** — free to use, modify, and distribute.

---

<div align="center">

Made with ❤️ by [Alirewa](https://github.com/Alirewa)

</div>
