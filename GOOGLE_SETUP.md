# Google Cloud Console Setup Guide

This guide walks you through everything needed to enable OAuth2 for this bot so users can authenticate their personal Google Drive (15 GB).

---

## Step 1 — Create a Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click the project selector (top-left) → **New Project**
3. Name it (e.g., `TG Drive Uploader Bot`) → **Create**
4. Wait for the project to be created, then select it

---

## Step 2 — Enable the Google Drive API

1. In the left sidebar → **APIs & Services** → **Library**
2. Search for **Google Drive API**
3. Click it → **Enable**

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
> To allow all users, submit the app for **Verification** (or simply publish without sensitive scopes — `drive.file` does not require verification).

---

## Step 4 — Create OAuth 2.0 Credentials

1. **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth client ID**
3. **Application type**: `Web application`
4. **Name**: `Telegram Bot Client` (or any name)

### ✅ Authorized Redirect URIs — Critical Step

5. Under **Authorized redirect URIs**, click **+ Add URI**
6. Enter exactly:
   ```
   http://localhost
   ```
7. Click **Create**

> **Why `http://localhost`?**  
> The bot has no web server. When a user authorizes in their browser, Google redirects them to `http://localhost/?code=XXXX`. The page fails to load (nothing is listening on localhost), but the user can see the full URL in their browser's address bar. They copy that URL and paste it back into the Telegram chat. The bot extracts the `code` parameter and exchanges it for OAuth tokens.  
> This is a standard approach for CLI/bot OAuth flows that don't host a callback server.

---

## Step 5 — Copy Your Credentials

After creating the OAuth client, a dialog shows your credentials:

| Field | Where to copy |
|---|---|
| **Client ID** | `.env` → `GOOGLE_OAUTH_CLIENT_ID` |
| **Client Secret** | `.env` → `GOOGLE_OAUTH_CLIENT_SECRET` |

Your `.env` should look like:
```env
GOOGLE_OAUTH_CLIENT_ID=123456789-abcdef.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxx
GOOGLE_OAUTH_REDIRECT_URI=http://localhost
```

---

## Step 6 — Publish the App (Remove Test-User Restriction)

If you want any Telegram user (not just test users) to be able to authenticate:

1. **OAuth consent screen** → **Publishing status**
2. Click **Publish App** → confirm
3. Since you're only using `drive.file` (not a restricted scope), Google does **not** require a formal review

---

## Step 7 — Verification Checklist

Before starting the bot, confirm:

- [ ] Google Drive API is **Enabled**
- [ ] OAuth consent screen status is **In production** (or you added test users)
- [ ] Authorized Redirect URI is exactly `http://localhost` (no trailing slash, no port)
- [ ] `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` are set in `.env`
- [ ] `GOOGLE_OAUTH_REDIRECT_URI=http://localhost` is set in `.env`

### Test the Flow
1. Start the bot, send `/start`, choose language
2. Tap **Authenticate Google Drive**
3. Open the link → sign in → grant permission
4. Copy the full URL from the browser address bar (it will start with `http://localhost/?code=`)
5. Paste it into the Telegram chat
6. Bot should reply: **"Google Drive Authenticated!"**
7. Send any file — it should upload to your Drive and return a shareable link

---

## Troubleshooting

| Error | Fix |
|---|---|
| `redirect_uri_mismatch` | Redirect URI in Google Console must be **exactly** `http://localhost` |
| `access_denied` | Make sure your Google account is added as a Test User (if app is in Testing) |
| `invalid_client` | Double-check Client ID and Secret in `.env` |
| `Token has been expired or revoked` | User needs to re-authenticate; tap **Re-authenticate** in the bot |
| `This app isn't verified` | Click **Advanced** → **Go to [App Name] (unsafe)** — safe to do for your own bot |
