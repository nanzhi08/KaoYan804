from __future__ import annotations

from dataclasses import dataclass
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from .time_utils import utc_now_naive


@dataclass(frozen=True)
class Migration:
    version: str
    description: str
    statements: tuple[str, ...]


MIGRATIONS: tuple[Migration, ...] = (
    Migration(
        version="20260609_0001_schema_migrations",
        description="Track applied database migrations",
        statements=(),
    ),
    Migration(
        version="20260629_0003_fix_knowledge_mastery_unique",
        description="Remove unique on knowledge_point_id, add composite unique on (user_id, knowledge_point_id)",
        statements=(
            "DROP INDEX IF EXISTS ix_knowledge_mastery_knowledge_point_id",
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_user_knowledge_point ON knowledge_mastery(user_id, knowledge_point_id)",
        ),
    ),
    Migration(
        version="20260629_0002_user_isolation",
        description="Add user_id columns for multi-user isolation",
        statements=(
            "ALTER TABLE practice_records ADD COLUMN user_id INTEGER REFERENCES users(id)",
            "ALTER TABLE knowledge_mastery ADD COLUMN user_id INTEGER REFERENCES users(id)",
            "ALTER TABLE ai_conversations ADD COLUMN user_id INTEGER REFERENCES users(id)",
            "ALTER TABLE ai_feedbacks ADD COLUMN user_id INTEGER REFERENCES users(id)",
            "ALTER TABLE ai_training_examples ADD COLUMN user_id INTEGER REFERENCES users(id)",
            "ALTER TABLE mock_exams ADD COLUMN user_id INTEGER REFERENCES users(id)",
            "ALTER TABLE documents ADD COLUMN user_id INTEGER REFERENCES users(id)",
        ),
    ),

)


async def _ensure_migration_table(conn: AsyncConnection) -> None:
    await conn.execute(text(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(64) PRIMARY KEY,
            description VARCHAR(255) NOT NULL,
            applied_at DATETIME NOT NULL
        )
        """
    ))


async def _applied_versions(conn: AsyncConnection) -> set[str]:
    result = await conn.execute(text("SELECT version FROM schema_migrations"))
    return {row[0] for row in result.fetchall()}


async def run_migrations(conn: AsyncConnection) -> list[str]:
    await _ensure_migration_table(conn)
    applied = await _applied_versions(conn)
    newly_applied: list[str] = []

    for migration in MIGRATIONS:
        if migration.version in applied:
            continue

        for statement in migration.statements:
            try:
                await conn.execute(text(statement))
            except Exception:
                # Column may already exist from model definitions
                pass

        await conn.execute(
            text(
                """
                INSERT INTO schema_migrations (version, description, applied_at)
                VALUES (:version, :description, :applied_at)
                """
            ),
            {
                "version": migration.version,
                "description": migration.description,
                "applied_at": utc_now_naive().isoformat(sep=" "),
            },
        )
        newly_applied.append(migration.version)

    return newly_applied
