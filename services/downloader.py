"""
External URL downloader using yt-dlp.
Supports YouTube, Instagram, Twitter/X, TikTok, Vimeo, SoundCloud, Dailymotion, and many others.

All blocking I/O runs in a thread-pool executor; progress callbacks are
scheduled back onto the asyncio event loop via run_coroutine_threadsafe.
"""
import asyncio
import logging
import os
import re
from typing import Callable, Coroutine, Optional

import requests

logger = logging.getLogger(__name__)

# ── Platform detection ────────────────────────────────────────────────────────

PLATFORM_PATTERNS: dict[str, list[str]] = {
    "YouTube":     [r"youtube\.com/watch", r"youtu\.be/", r"youtube\.com/shorts/", r"youtube\.com/live/"],
    "Instagram":   [r"instagram\.com/p/", r"instagram\.com/reel/", r"instagram\.com/tv/", r"instagram\.com/stories/"],
    "Twitter/X":   [r"twitter\.com/\w+/status/", r"x\.com/\w+/status/"],
    "TikTok":      [r"tiktok\.com/"],
    "Vimeo":       [r"vimeo\.com/\d"],
    "SoundCloud":  [r"soundcloud\.com/[\w-]+/[\w-]+"],
    "Dailymotion": [r"dailymotion\.com/video/"],
    "MediaFire":   [r"mediafire\.com/file/", r"mediafire\.com/download/"],
    "Dropbox":     [r"dropbox\.com/"],
    "WeTransfer":  [r"we\.tl/", r"wetransfer\.com/downloads/"],
}

PLATFORM_ICONS: dict[str, str] = {
    "YouTube":     "🎬",
    "Instagram":   "📸",
    "Twitter/X":   "🐦",
    "TikTok":      "🎵",
    "Vimeo":       "🎥",
    "SoundCloud":  "🎵",
    "Dailymotion": "🎬",
    "MediaFire":   "📦",
    "Dropbox":     "📦",
    "WeTransfer":  "📦",
    "Direct":      "🔗",
}

# Detect direct file links by extension
_DIRECT_FILE_EXT = re.compile(
    r'\.(mp4|mkv|webm|avi|mov|mp3|m4a|wav|flac|ogg|opus|'
    r'zip|rar|7z|pdf|docx|xlsx|pptx|png|jpg|jpeg|gif|webp)(\?.*)?$',
    re.IGNORECASE,
)

# yt-dlp format strings per quality key (no ffmpeg required — progressive streams)
_YT_QUALITY_FORMATS: dict[str, str] = {
    "best":  "best[ext=mp4]/best[ext=webm]/best",
    "720":   "best[height<=720][ext=mp4]/best[height<=720]/best",
    "480":   "best[height<=480][ext=mp4]/best[height<=480]/best",
    "audio": "bestaudio[ext=m4a]/bestaudio[ext=opus]/bestaudio",
}


def detect_source(url: str) -> Optional[str]:
    """Return the platform name, or None if not recognised."""
    for platform, patterns in PLATFORM_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return platform
    # Detect direct file links by URL extension
    if _DIRECT_FILE_EXT.search(url):
        return "Direct"
    return None


def source_icon(platform: str) -> str:
    return PLATFORM_ICONS.get(platform, "🌐")


# ── Core download (runs in executor) ─────────────────────────────────────────

def _ytdlp_result(ydl, info: dict, output_dir: str) -> tuple[str, str]:
    """Extract (file_path, title) from a completed yt-dlp download."""
    title: str = info.get("title") or "download"
    file_path: str = ydl.prepare_filename(info)
    if not os.path.exists(file_path):
        base = os.path.splitext(file_path)[0]
        for ext in ("mp4", "mkv", "webm", "mp3", "m4a", "opus", "ogg"):
            candidate = f"{base}.{ext}"
            if os.path.exists(candidate):
                file_path = candidate
                break
    return file_path, title


def _run_ytdlp(
    url: str,
    output_dir: str,
    quality_key: str = "best",
    on_progress: Optional[Callable[..., Coroutine]] = None,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> tuple[str, str]:
    """
    Download *url* with yt-dlp.

    YouTube strategy (VPS-safe, no cookies required):
      1. iOS player client  — bypasses bot-detection for most public videos
      2. Android embedded client — second attempt if iOS fails
      3. Default client with cookies if YTDLP_COOKIES_FILE is set
      4. pytubefix — final fallback for YouTube
    Non-YouTube: single yt-dlp attempt, no special client needed.
    """
    import yt_dlp
    from config import YTDLP_COOKIES_FILE

    def _hook(d: dict) -> None:
        if d["status"] == "downloading" and on_progress and loop:
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            if total > 0:
                try:
                    asyncio.run_coroutine_threadsafe(on_progress(downloaded, total), loop)
                except Exception:
                    pass

    fmt = _YT_QUALITY_FORMATS.get(quality_key, "best[ext=mp4]/best[ext=webm]/best")
    outtmpl = os.path.join(output_dir, "%(id)s.%(ext)s")
    is_youtube = bool(re.search(r'youtube\.com|youtu\.be', url, re.IGNORECASE))

    base_opts: dict = {
        "format": fmt,
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "progress_hooks": [_hook],
    }

    if is_youtube:
        # ── Attempt 1: iOS client (most reliable on VPS, no cookies needed) ──
        ios_opts = {
            **base_opts,
            "extractor_args": {"youtube": {"player_client": ["ios"]}},
        }
        try:
            with yt_dlp.YoutubeDL(ios_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return _ytdlp_result(ydl, info, output_dir)
        except Exception as e1:
            logger.warning("yt-dlp iOS client failed: %s", e1)

        # ── Attempt 2: Android embedded client ────────────────────────────────
        android_opts = {
            **base_opts,
            "extractor_args": {"youtube": {"player_client": ["android_embedded"]}},
        }
        try:
            with yt_dlp.YoutubeDL(android_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return _ytdlp_result(ydl, info, output_dir)
        except Exception as e2:
            logger.warning("yt-dlp android_embedded failed: %s", e2)

        # ── Attempt 3: default client + cookies (if configured) ───────────────
        cookie_opts = dict(base_opts)
        if YTDLP_COOKIES_FILE and os.path.isfile(YTDLP_COOKIES_FILE):
            cookie_opts["cookiefile"] = YTDLP_COOKIES_FILE
        try:
            with yt_dlp.YoutubeDL(cookie_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return _ytdlp_result(ydl, info, output_dir)
        except Exception as e3:
            logger.warning("yt-dlp default client failed: %s", e3)

        # ── Attempt 4: pytubefix ──────────────────────────────────────────────
        logger.warning("All yt-dlp attempts failed for YouTube — trying pytubefix")
        return _run_pytubefix(url, output_dir)

    # ── Non-YouTube: single attempt ───────────────────────────────────────────
    if YTDLP_COOKIES_FILE and os.path.isfile(YTDLP_COOKIES_FILE):
        base_opts["cookiefile"] = YTDLP_COOKIES_FILE
    with yt_dlp.YoutubeDL(base_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return _ytdlp_result(ydl, info, output_dir)


def _run_pytubefix(url: str, output_dir: str) -> tuple[str, str]:
    """
    Fallback YouTube downloader using pytubefix.
    Tries WEB client first (most compatible), then IOS client.
    """
    from pytubefix import YouTube

    last_exc: Exception | None = None
    for client in ("WEB", "IOS", "MWEB"):
        try:
            yt = YouTube(url, client=client, use_oauth=False, allow_oauth_cache=False)
            title = yt.title or "video"
            stream = (
                yt.streams
                .filter(progressive=True, file_extension="mp4")
                .order_by("resolution")
                .desc()
                .first()
            ) or yt.streams.get_highest_resolution()
            if not stream:
                raise ValueError(f"pytubefix ({client}): no downloadable stream found")
            logger.info("pytubefix (%s): downloading '%s'", client, title)
            path = stream.download(output_path=output_dir)
            return path, title
        except Exception as exc:
            logger.warning("pytubefix %s failed: %s", client, exc)
            last_exc = exc

    raise ValueError(f"pytubefix: all clients failed — {last_exc}")


# ── Async wrapper ─────────────────────────────────────────────────────────────

async def download_url(
    url: str,
    output_dir: str,
    quality_key: str = "best",
    on_progress: Optional[Callable[..., Coroutine]] = None,
) -> tuple[str, str]:
    """
    Download *url* using yt-dlp (with pytubefix fallback for YouTube).
    Returns (file_path, title).  Raises on failure.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, _run_ytdlp, url, output_dir, quality_key, on_progress, loop
    )


# ── Cobalt.tools API downloader ───────────────────────────────────────────────

_COBALT_API = "https://api.cobalt.tools/"
_COBALT_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# videoQuality values accepted by cobalt: max, 4320, 2160, 1440, 1080, 720, 480, 360, 240, 144
_COBALT_QUALITY_MAP = {
    "best":  "max",
    "1080":  "1080",
    "720":   "720",
    "480":   "480",
    "audio": None,   # audio-only mode
}


def _run_cobalt(url: str, output_dir: str, quality_key: str = "best") -> tuple[str, str]:
    """
    Download via cobalt.tools public API.
    quality_key: 'best' | '1080' | '720' | '480' | 'audio'
    Returns (file_path, title).
    """
    import time

    audio_only = (quality_key == "audio")
    payload: dict = {"url": url}
    if audio_only:
        payload["downloadMode"] = "audio"
        payload["audioFormat"]  = "mp3"
    else:
        payload["videoQuality"] = _COBALT_QUALITY_MAP.get(quality_key, "max")

    sess = requests.Session()
    sess.headers.update({"User-Agent": "Mozilla/5.0"})

    resp = sess.post(_COBALT_API, json=payload, headers=_COBALT_HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    status = data.get("status")
    if status == "error":
        code = data.get("error", {}).get("code", "unknown")
        raise ValueError(f"cobalt error: {code}")

    if status not in ("tunnel", "redirect", "stream"):
        raise ValueError(f"cobalt unexpected status: {status} — {data}")

    dl_url  = data.get("url") or data.get("tunnel")
    filename = data.get("filename") or f"cobalt_{int(time.time())}.{'mp3' if audio_only else 'mp4'}"
    # Sanitise filename
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

    logger.info("cobalt: downloading %s (%s)", filename, quality_key)
    r = sess.get(dl_url, stream=True, timeout=300)
    r.raise_for_status()

    path = os.path.join(output_dir, filename)
    with open(path, "wb") as f:
        for chunk in r.iter_content(65536):
            if chunk:
                f.write(chunk)

    title = os.path.splitext(filename)[0]
    return path, title


async def download_via_cobalt(
    url: str,
    output_dir: str,
    quality_key: str = "best",
) -> tuple[str, str]:
    """Async wrapper around _run_cobalt. Returns (file_path, title)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _run_cobalt, url, output_dir, quality_key)


# ── Google Drive public file downloader ───────────────────────────────────────

_GDRIVE_PATTERNS = [
    re.compile(r"drive\.google\.com/file/d/([a-zA-Z0-9_-]+)"),
    re.compile(r"drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)"),
    re.compile(r"drive\.google\.com/uc\?.*id=([a-zA-Z0-9_-]+)"),
]


def extract_gdrive_id(url: str) -> Optional[str]:
    """Return the file ID from a Google Drive URL, or None."""
    for pattern in _GDRIVE_PATTERNS:
        m = pattern.search(url)
        if m:
            return m.group(1)
    return None


def _run_gdrive_download(file_id: str, output_dir: str) -> tuple[str, str]:
    """
    Blocking download of a public Google Drive file using gdown.
    Returns (file_path, filename).  Raises ValueError on failure.
    gdown handles virus-scan confirmation, large files, and redirects automatically.
    """
    import gdown

    url = f"https://drive.google.com/uc?id={file_id}"
    # output must end with "/" so gdown picks the filename from Google Drive
    out_dir = output_dir.rstrip("/") + "/"
    output = gdown.download(url=url, output=out_dir, quiet=True)

    if not output or not os.path.exists(output):
        raise ValueError(
            "Download failed — the file may be private, removed, or access was denied."
        )

    filename = os.path.basename(output)
    # Sanitise just in case
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename) or f"{file_id}.bin"
    return output, filename


async def download_gdrive(file_id: str, output_dir: str) -> tuple[str, str]:
    """Async wrapper around _run_gdrive_download. Returns (file_path, filename)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _run_gdrive_download, file_id, output_dir)


# ── Generic direct-link downloader ────────────────────────────────────────────

def _run_direct_download(url: str, output_dir: str) -> tuple[str, str]:
    """
    Fallback downloader for plain HTTP/HTTPS file links.
    Derives filename from Content-Disposition or the URL path.
    """
    import time as _time
    from urllib.parse import urlparse, unquote

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, stream=True, timeout=300, allow_redirects=True)
    resp.raise_for_status()

    # Derive filename from Content-Disposition header first
    cd = resp.headers.get("Content-Disposition", "")
    filename = ""
    if cd:
        m = re.search(r'filename[^;=\n]*=(["\']?)([^"\'\n;]+)\1', cd)
        if m:
            filename = m.group(2).strip()
    if not filename:
        path = urlparse(resp.url).path
        filename = unquote(os.path.basename(path.split("?")[0]))
    if not filename:
        filename = f"download_{int(_time.time())}.bin"
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

    dest = os.path.join(output_dir, filename)
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(65536):
            if chunk:
                f.write(chunk)

    title = os.path.splitext(filename)[0]
    return dest, title


async def download_direct(url: str, output_dir: str) -> tuple[str, str]:
    """Async wrapper around _run_direct_download. Returns (file_path, title)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _run_direct_download, url, output_dir)
