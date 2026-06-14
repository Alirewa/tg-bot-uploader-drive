# Google Cloud Console Setup Guide

This guide walks you through everything needed to enable OAuth2 so users can authenticate their personal Google Drive (15 GB free).

---

> ⚠️ **Common Mistake — Enable the correct API!**  
> You must enable **Google Drive API**.  
> Do **NOT** enable "Local Services API", "Drive Enterprise", or anything else with "Drive" in the name.  
> The exact name is: **Google Drive API** — search for it precisely.

---

## Step 1 — Create a Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click the project selector (top-left) → **New Project**
3. Name it (e.g., `TG Drive Bot`) → **Create**
4. Wait for the project to be created, then select it

---

## Step 2 — Enable the Google Drive API

1. In the left sidebar → **APIs & Services** → **Library**
2. In the search box type: `Google Drive API`
3. Click the result titled exactly **"Google Drive API"**
4. Click **Enable**

> ✅ After enabling, the page should show **"API enabled"** with a blue checkmark.  
> If you see a different API name in the URL or title — go back and search again.

---

## Step 3 — Configure the OAuth Consent Screen

1. **APIs & Services** → **OAuth consent screen**
2. Choose **External** → **Create**
3. Fill in the required fields:
   - **App name**: `Drive Uploader Bot` (or any name)
   - **User support email**: your Google account email
   - **Developer contact email**: your Google account email
4. Click **Save and Continue**

### Scopes
5. Click **Add or Remove Scopes**
6. Search for `drive.file` and check:
   - `https://www.googleapis.com/auth/drive.file`
   - _(This scope only lets the bot read/write files it uploads — it cannot access other files in the user's Drive)_
7. Click **Update** → **Save and Continue**

### Test Users (while in Testing status)
8. Add your own Google account as a test user so you can verify everything works
9. Click **Save and Continue** → **Back to Dashboard**

> **Note:** While the app is in "Testing" status, only accounts you add as Test Users can authorize.  
> To allow all users, publish the app (Step 6 below). Since `drive.file` is not a restricted scope, Google does **not** require a formal review.

---

## Step 4 — Create OAuth 2.0 Credentials

1. **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth client ID**
3. **Application type**: `Web application`
4. **Name**: `Telegram Bot Client` (or any name)

### ✅ Authorized Redirect URIs — Critical Step

You must add the correct redirect URI depending on which mode you want:

**Choose one:**

| Mode | Redirect URI to add | When to use |
|---|---|---|
| **Auto (Recommended)** | `http://YOUR_SERVER_IP:8080/oauth/callback` | Bot is on a VPS/server with a public IP |
| **Manual (Fallback)** | `http://localhost` | Local testing or no public IP |

> You can add **both** URIs at the same time — they won't conflict.

5. Under **Authorized redirect URIs**, click **+ Add URI** and add your chosen URI(s)
6. Click **Create**

---

## Step 5 — Copy Your Credentials

After creating the OAuth client, a dialog shows your credentials:

| Field | Where to copy |
|---|---|
| **Client ID** | `.env` → `GOOGLE_OAUTH_CLIENT_ID` |
| **Client Secret** | `.env` → `GOOGLE_OAUTH_CLIENT_SECRET` |

---

## Step 6 — Configure Your `.env`

### Option A — Automatic OAuth (Recommended for servers)

The bot starts an HTTP server on port 8080. When the user clicks "Authenticate", they just approve in the browser — the bot detects the confirmation automatically and links their account. No copy-pasting needed.

```env
GOOGLE_OAUTH_CLIENT_ID=123456789-abcdef.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxx
GOOGLE_OAUTH_REDIRECT_URI=http://YOUR_SERVER_IP:8080/oauth/callback
OAUTH_SERVER_PORT=8080
```

**Also open the firewall port:**
```bash
sudo ufw allow 8080
# or if using iptables:
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

> Replace `YOUR_SERVER_IP` with your actual VPS/server public IP address (e.g., `http://45.62.100.12:8080/oauth/callback`).  
> The redirect URI in your `.env` must **exactly** match what you added in Google Console.

### Option B — Manual OAuth (Fallback)

The user clicks the link, approves, then copies the `http://localhost/?code=...` URL from their browser and pastes it into the Telegram chat.

```env
GOOGLE_OAUTH_CLIENT_ID=123456789-abcdef.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxx
GOOGLE_OAUTH_REDIRECT_URI=http://localhost
```

> `AUTO_OAUTH` is automatically set based on the redirect URI — if it starts with `http://localhost`, manual mode is used; otherwise, auto mode activates.

---

## Step 7 — Publish the App (Remove Test-User Restriction)

If you want any Telegram user (not just test users) to be able to authenticate:

1. **OAuth consent screen** → **Publishing status**
2. Click **Publish App** → confirm
3. Since you're only using `drive.file` (not a restricted scope), Google does **not** require a formal review

---

## Step 8 — Verification Checklist

Before starting the bot, confirm:

- [ ] **Google Drive API** is Enabled (exact name — not "Local Services API")
- [ ] OAuth consent screen status is **In production** (or test users are added)
- [ ] Redirect URI in Google Console **exactly matches** what's in `.env`
- [ ] `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` are set in `.env`
- [ ] For Auto mode: port 8080 is open in the firewall

### Test the Flow (Auto Mode)
1. Start the bot → send `/start` → choose language
2. Tap **Authenticate Google Drive** → click the link
3. Sign in with your Google account → grant permission
4. Browser shows: **"Google Drive Connected!"** page
5. Bot automatically sends a success message in Telegram
6. Send any file → it uploads to your Drive with a shareable link

### Test the Flow (Manual Mode)
1. Start the bot → send `/start` → choose language
2. Tap **Authenticate Google Drive** → click the link
3. Sign in → grant permission
4. Page fails to load (expected) — copy the **full URL** from your browser's address bar
   - It will start with: `http://localhost/?code=`
5. Paste that URL into the Telegram chat
6. Bot should reply: **"Google Drive Authenticated!"**
7. Send any file — it should upload and return a shareable link

---

## Troubleshooting

| Error | Fix |
|---|---|
| `redirect_uri_mismatch` | Redirect URI in Google Console must **exactly** match `.env`. No trailing slash, correct port. |
| `access_denied` | Add your Google account as a Test User (if app is in Testing mode) |
| `invalid_client` | Double-check Client ID and Secret in `.env` |
| `Token has been expired or revoked` | User re-taps **Authenticate Google Drive** in the bot |
| `This app isn't verified` | Click **Advanced** → **Go to [App Name] (unsafe)** — this is normal for personal bots |
| Bot doesn't detect auto auth | Check that port 8080 is open; check that redirect URI matches exactly |
| Wrong API enabled | Go to APIs & Services → Enabled APIs → verify "Google Drive API" is listed |
