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
            await conn.execute(text(statement))

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
