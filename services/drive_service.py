"""
Google Drive integration — personal-drive (OAuth2) only.

All blocking I/O runs in a thread-pool executor; progress callbacks are
scheduled back onto the asyncio event loop via run_coroutine_threadsafe.
"""
import asyncio
import logging
import os
from typing import Callable, Coroutine, Optional

import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from config import (
    GOOGLE_OAUTH_CLIENT_ID,
    GOOGLE_OAUTH_CLIENT_SECRET,
    GOOGLE_OAUTH_REDIRECT_URI,
)

logger = logging.getLogger(__name__)

DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]
UPLOAD_CHUNK_SIZE = 5 * 1024 * 1024  # 5 MB


# ── User service builder ──────────────────────────────────────────────────────

def build_user_service(access_token: str, refresh_token: str) -> tuple:
    """
    Return (service, current_access_token).
    Automatically refreshes the access token if it has expired.
    """
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_OAUTH_CLIENT_ID,
        client_secret=GOOGLE_OAUTH_CLIENT_SECRET,
        scopes=DRIVE_SCOPES,
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(google.auth.transport.requests.Request())
    return build("drive", "v3", credentials=creds, cache_discovery=False), creds.token


# ── OAuth2 flow ───────────────────────────────────────────────────────────────

def create_oauth_flow() -> Flow:
    client_config = {
        "web": {
            "client_id": GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uris": [GOOGLE_OAUTH_REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    return Flow.from_client_config(
        client_config, scopes=DRIVE_SCOPES, redirect_uri=GOOGLE_OAUTH_REDIRECT_URI
    )


def get_auth_url(flow: Flow) -> str:
    url, _ = flow.authorization_url(
        access_type="offline", prompt="consent", include_granted_scopes="true"
    )
    return url


# ── Synchronous upload (runs in executor) ─────────────────────────────────────

def sync_upload(
    file_path: str,
    file_name: str,
    service,
    async_progress_cb: Optional[Callable[..., Coroutine]],
    loop: asyncio.AbstractEventLoop,
) -> tuple[str, str]:
    """
    Upload *file_path* to Google Drive and return (file_id, share_link).
    Fires *async_progress_cb(current_bytes, total_bytes)* on each chunk via the
    event loop.
    """
    file_size = os.path.getsize(file_path)
    media = MediaFileUpload(file_path, resumable=True, chunksize=UPLOAD_CHUNK_SIZE)
    request = service.files().create(
        body={"name": file_name},
        media_body=media,
        fields="id",
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status and async_progress_cb:
            try:
                asyncio.run_coroutine_threadsafe(
                    async_progress_cb(int(status.resumable_progress), file_size), loop
                )
            except Exception:
                pass

    file_id: str = response["id"]

    # Make publicly readable with the link
    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()

    info = service.files().get(fileId=file_id, fields="webViewLink").execute()
    share_link: str = info.get(
        "webViewLink", f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    )
    return file_id, share_link


def sync_delete(file_id: str, service) -> bool:
    """Delete a Drive file. Returns True on success."""
    try:
        service.files().delete(fileId=file_id).execute()
        return True
    except HttpError as exc:
        logger.error("Drive delete failed for %s: %s", file_id, exc)
        return False
