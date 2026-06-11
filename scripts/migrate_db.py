"""Run lightweight SQLite migrations for the 804 knowledge base."""
import sys

sys.path.insert(0, "backend")

import asyncio

from app.database import engine
from app.migrations import run_migrations


async def main() -> None:
    async with engine.begin() as conn:
        applied = await run_migrations(conn)

    if applied:
        print("Applied migrations:")
        for version in applied:
            print(f"  - {version}")
    else:
        print("Database schema is up to date.")


if __name__ == "__main__":
    asyncio.run(main())
