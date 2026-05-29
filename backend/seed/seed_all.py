"""Auto-seed: populate empty database on first startup.

Strategy:
1. Check if DB exists in DATA_DIR
2. If not, copy bundled seed database (1283 questions + 141 knowledge points)
3. If bundled DB not found, fall back to running seed scripts
"""
import os
import shutil
import asyncio
from pathlib import Path

from app.config import settings
from app.database import async_session, init_db
from sqlalchemy import text


# Bundled seed database (2MB, full dataset)
BUNDLED_DB = Path(__file__).parent / "knowledge.db"


async def seed_all():
    target_db = Path(settings.DATABASE_URL.replace("sqlite+aiosqlite:///", ""))

    # If target DB already exists and has data, skip
    if target_db.exists():
        await init_db()
        async with async_session() as db:
            result = await db.execute(text("SELECT COUNT(*) FROM knowledge_points"))
            if result.scalar() > 0:
                print(f"[Seed] Database exists with data, skipping.")
                return
        print("[Seed] DB file exists but empty, will re-seed.")

    # Strategy 1: Copy bundled database
    if BUNDLED_DB.exists():
        print(f"[Seed] Copying bundled database ({BUNDLED_DB.stat().st_size/1024:.0f}KB)...")
        target_db.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(BUNDLED_DB, target_db)
        await init_db()
        async with async_session() as db:
            result = await db.execute(text("SELECT COUNT(*) FROM knowledge_points"))
            kp_count = result.scalar()
            result2 = await db.execute(text("SELECT COUNT(*) FROM questions"))
            q_count = result2.scalar()
        print(f"[Seed] Done: {kp_count} knowledge points, {q_count} questions.")
        return

    # Strategy 2: Fallback - run seed scripts (for dev environments)
    print("[Seed] No bundled DB found. Running seed scripts instead...")

    try:
        from seed import seed_knowledge
        await seed_knowledge.seed()
        print("[Seed] seed_knowledge done.")
    except Exception as e:
        print(f"[Seed] seed_knowledge failed: {e}")

    try:
        from seed import seed_questions
        await seed_questions.seed()
        print("[Seed] seed_questions done.")
    except Exception as e:
        print(f"[Seed] seed_questions failed: {e}")

    try:
        from seed import seed_knowledge_extended
        await seed_knowledge_extended.seed()
        print("[Seed] seed_knowledge_extended done.")
    except Exception as e:
        print(f"[Seed] seed_knowledge_extended failed: {e}")

    print("[Seed] Seed scripts completed.")


if __name__ == "__main__":
    asyncio.run(seed_all())
