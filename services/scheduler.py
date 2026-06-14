"""
Background scheduler:
  1. Cleans up bot-drive (Google Drive) files older than CLEANUP_AFTER_HOURS
     — only when BOT_DRIVE_SA_JSON is configured.
  2. Cleans up orphaned temp files on disk older than 2 hours
     — always runs, protects server disk from crash leftovers.
"""
import asyncio
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from config import BOT_DRIVE_SA_JSON, CLEANUP_AFTER_HOURS, TEMP_DIR
from database.models import Upload
from database.session import AsyncSessionLocal
from services.drive_service import build_bot_service, sync_delete

logger = logging.getLogger(__name__)

_scheduler = AsyncIOScheduler()

# Temp files older than this are considered orphaned (bot crashed mid-upload)
_TEMP_MAX_AGE_SECONDS = 2 * 60 * 60  # 2 hours


async def _cleanup_temp_dir() -> None:
    """Delete any file in the temp directory that is older than 2 hours."""
    now = time.time()
    removed = 0
    try:
        for entry in os.scandir(TEMP_DIR):
            if not entry.is_file():
                continue
            try:
                age = now - entry.stat().st_mtime
                if age > _TEMP_MAX_AGE_SECONDS:
                    os.unlink(entry.path)
                    removed += 1
            except Exception as exc:
                logger.warning("Scheduler: could not remove temp file %s: %s", entry.path, exc)
    except Exception as exc:
        logger.error("Scheduler: temp-dir scan failed: %s", exc)
    if removed:
        logger.info("Scheduler: removed %d orphaned temp file(s) older than 2h", removed)


async def _cleanup_bot_drive() -> None:
    if not BOT_DRIVE_SA_JSON:
        return

    cutoff = datetime.now(timezone.utc) - timedelta(hours=CLEANUP_AFTER_HOURS)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Upload).where(
                Upload.is_personal_drive.is_(False),
                Upload.is_deleted.is_(False),
                Upload.uploaded_at < cutoff,
            )
        )
        old_files = result.scalars().all()

    if not old_files:
        return

    try:
        service = build_bot_service()
    except Exception as exc:
        logger.error("Scheduler: could not build bot drive service: %s", exc)
        return

    deleted = 0
    for upload in old_files:
        try:
            loop = asyncio.get_event_loop()
            ok = await loop.run_in_executor(
                None, sync_delete, upload.gdrive_file_id, service
            )
            if ok:
                async with AsyncSessionLocal() as session:
                    u = await session.get(Upload, upload.id)
                    if u:
                        u.is_deleted = True
                        await session.commit()
                deleted += 1
        except Exception as exc:
            logger.error("Scheduler: failed to delete file %s: %s", upload.gdrive_file_id, exc)

    if deleted:
        logger.info("Scheduler: cleaned up %d bot-drive file(s) older than %dh",
                    deleted, CLEANUP_AFTER_HOURS)


def start_scheduler() -> None:
    # Temp-dir cleanup runs always (protects server disk)
    _scheduler.add_job(_cleanup_temp_dir, "interval", minutes=30, id="temp_cleanup")
    logger.info("Scheduler: temp-dir cleanup every 30 min (max age 2h)")

    if BOT_DRIVE_SA_JSON:
        _scheduler.add_job(_cleanup_bot_drive, "interval", hours=1, id="bot_drive_cleanup")
        logger.info("Scheduler: bot-drive cleanup every 1h (cutoff %dh)", CLEANUP_AFTER_HOURS)

    _scheduler.start()
