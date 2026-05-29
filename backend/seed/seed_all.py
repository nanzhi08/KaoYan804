"""Auto-seed: populate empty database on first startup."""
import sys
import asyncio

from app.database import async_session, init_db
from sqlalchemy import text


async def is_db_empty() -> bool:
    async with async_session() as db:
        result = await db.execute(text("SELECT COUNT(*) FROM knowledge_points"))
        return result.scalar() == 0


async def seed_all():
    if not await is_db_empty():
        print("[Seed] Database already populated, skipping.")
        return

    print("[Seed] Empty database detected. Running seed scripts...")

    # seed_knowledge.py - async def seed()
    try:
        from seed import seed_knowledge
        await seed_knowledge.seed()
        print("[Seed] seed_knowledge done.")
    except Exception as e:
        print(f"[Seed] seed_knowledge failed: {e}")

    # seed_questions.py - async def seed()
    try:
        from seed import seed_questions
        await seed_questions.seed()
        print("[Seed] seed_questions done.")
    except Exception as e:
        print(f"[Seed] seed_questions failed: {e}")

    # seed_knowledge_extended.py - async def seed()
    try:
        from seed import seed_knowledge_extended
        await seed_knowledge_extended.seed()
        print("[Seed] seed_knowledge_extended done.")
    except Exception as e:
        print(f"[Seed] seed_knowledge_extended failed: {e}")

    # seed_ds_markdown_full.py - async def run_import(dry_run=False)
    try:
        from seed import seed_ds_markdown_full
        await seed_ds_markdown_full.run_import(dry_run=False)
        print("[Seed] seed_ds_markdown_full done.")
    except Exception as e:
        print(f"[Seed] seed_ds_markdown_full failed: {e}")

    print("[Seed] All seed scripts completed.")


if __name__ == "__main__":
    asyncio.run(seed_all())
