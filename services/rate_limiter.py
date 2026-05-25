from datetime import datetime
from sqlalchemy import select
from database.models import RateLimit
from database.session import AsyncSessionLocal
from config import RATE_LIMIT_MAX_UPLOADS, RATE_LIMIT_WINDOW_SECONDS


async def check_rate_limit(user_id: int) -> tuple[bool, int]:
    """
    Returns (is_limited, wait_seconds).
    is_limited=True means the user must wait wait_seconds before uploading.
    """
    now = datetime.utcnow()
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(RateLimit).where(RateLimit.user_id == user_id))
        rl = result.scalars().first()

        if not rl:
            return False, 0

        elapsed = (now - rl.window_start).total_seconds()
        if elapsed >= RATE_LIMIT_WINDOW_SECONDS:
            # Window expired — reset (don't commit yet, update_rate_limit will do it)
            return False, 0

        if rl.upload_count >= RATE_LIMIT_MAX_UPLOADS:
            wait = int(RATE_LIMIT_WINDOW_SECONDS - elapsed)
            return True, wait

        return False, 0


async def update_rate_limit(user_id: int) -> None:
    """Increment the upload counter for the user, resetting window if expired."""
    now = datetime.utcnow()
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(RateLimit).where(RateLimit.user_id == user_id))
        rl = result.scalars().first()

        if not rl:
            session.add(RateLimit(user_id=user_id, upload_count=1, window_start=now))
        else:
            elapsed = (now - rl.window_start).total_seconds()
            if elapsed >= RATE_LIMIT_WINDOW_SECONDS:
                rl.upload_count = 1
                rl.window_start = now
            else:
                rl.upload_count += 1

        await session.commit()
