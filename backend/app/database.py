from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import logging

from .config import settings
from .migrations import run_migrations

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Fix legacy knowledge_mastery schema: remove column-level unique constraint
        # (SQLite internal unique indexes can't be dropped, so recreate the table)
        from sqlalchemy import text as _text
        try:
            result = await conn.execute(_text(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='knowledge_mastery'"
            ))
            ddl = result.scalar_one_or_none()
            if ddl and "UNIQUE (knowledge_point_id)" in ddl:
                await conn.execute(_text(
                    "CREATE TABLE IF NOT EXISTS knowledge_mastery_new ("
                    "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, "
                    "user_id INTEGER REFERENCES users(id), "
                    "knowledge_point_id INTEGER NOT NULL REFERENCES knowledge_points(id), "
                    "mastery_level FLOAT, ease_factor FLOAT, interval_days INTEGER, "
                    "repetitions INTEGER, total_attempts INTEGER, correct_attempts INTEGER, "
                    "last_reviewed_at DATETIME, next_review_at DATETIME, updated_at DATETIME, "
                    "UNIQUE(user_id, knowledge_point_id)"
                    ")"
                ))
                await conn.execute(_text(
                    "INSERT OR IGNORE INTO knowledge_mastery_new "
                    "(id, user_id, knowledge_point_id, mastery_level, ease_factor, interval_days, "
                    "repetitions, total_attempts, correct_attempts, last_reviewed_at, next_review_at, updated_at) "
                    "SELECT id, user_id, knowledge_point_id, mastery_level, ease_factor, interval_days, "
                    "repetitions, total_attempts, correct_attempts, last_reviewed_at, next_review_at, updated_at "
                    "FROM knowledge_mastery"
                ))
                await conn.execute(_text("DROP TABLE knowledge_mastery"))
                await conn.execute(_text("ALTER TABLE knowledge_mastery_new RENAME TO knowledge_mastery"))
        except Exception:
            pass
        try:
            await run_migrations(conn)
        except Exception:
            logger.exception("run_migrations failed, continuing startup")
