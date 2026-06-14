import logging
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from database.models import Base
from config import DATABASE_URL

logger = logging.getLogger(__name__)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, expire_on_commit=False
)

_NEW_USER_COLUMNS = [
    ("is_admin", "BOOLEAN DEFAULT 0"),
    ("upload_limit_exempt", "BOOLEAN DEFAULT 0"),
    ("referral_unlocked", "BOOLEAN DEFAULT 0"),
    ("referred_by_id", "BIGINT"),
    ("daily_upload_bytes", "BIGINT DEFAULT 0"),
    ("daily_upload_count", "INTEGER DEFAULT 0"),
    ("daily_reset_date", "VARCHAR(10)"),
]


async def _migrate(conn) -> None:
    for col_name, col_def in _NEW_USER_COLUMNS:
        try:
            await conn.exec_driver_sql(
                f"ALTER TABLE users ADD COLUMN {col_name} {col_def}"
            )
            logger.info("Migration: added column users.%s", col_name)
        except Exception:
            pass


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _migrate(conn)
    logger.info("Database tables verified / created")
