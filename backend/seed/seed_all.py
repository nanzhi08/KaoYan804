"""Auto-seed: populate empty database on first startup.

Strategy:
1. Check if DB exists in DATA_DIR
2. If DB exists and has knowledge_points → skip entirely
3. If DB exists but has no knowledge_points → ATTACH bundled DB and INSERT missing data
   (NEVER overwrite the live DB — it may contain user data)
4. If DB doesn't exist → copy bundled DB as starting point
"""
import os
import shutil
import sqlite3
import asyncio
from pathlib import Path

from app.config import settings
from app.database import async_session, init_db
from sqlalchemy import text


# Bundled seed database (~2MB, full dataset of knowledge_points + questions)
BUNDLED_DB = Path(__file__).parent / "knowledge.db"

# Tables that are safe to import from bundled DB (no user-specific data)
SEED_TABLES = [
    "knowledge_points",
    "questions",
    "question_knowledge_points",
]


async def _safe_import_seed_data(target_db: Path) -> None:
    """Import seed tables from bundled DB into live DB without overwriting.

    Copies bundled DB to a temp file first (avoids SQLite ATTACH lock issues),
    then uses raw sqlite3 to ATTACH+INSERT in a single connection.
    User tables (users, invite_codes, etc.) are never touched.
    """
    import tempfile
    # Copy bundled DB to a temp file to avoid locking the original
    tmp_path = Path(tempfile.gettempdir()) / f"_seed_import_{os.getpid()}.db"
    shutil.copy2(str(BUNDLED_DB), str(tmp_path))

    try:
        conn = sqlite3.connect(str(target_db))
        conn.execute(f"ATTACH DATABASE '{tmp_path}' AS bundled")
        for table in SEED_TABLES:
            try:
                conn.execute(
                    f"INSERT OR IGNORE INTO main.{table} SELECT * FROM bundled.{table}"
                )
                count = conn.execute(
                    f"SELECT COUNT(*) FROM {table}"
                ).fetchone()[0]
                print(f"[Seed]   {table}: {count} rows")
            except Exception as e:
                print(f"[Seed]   {table}: skipped ({e})")
        conn.commit()
        try:
            conn.execute("DETACH DATABASE bundled")
        except Exception:
            pass  # Windows SQLite may lock attached DB during INSERT...SELECT
        conn.close()
    finally:
        tmp_path.unlink(missing_ok=True)


async def seed_all():
    target_db = Path(settings.DATABASE_URL.replace("sqlite+aiosqlite:///", ""))

    # If target DB exists, check what's in it
    if target_db.exists():
        await init_db()
        needs_safe_import = False
        async with async_session() as db:
            result = await db.execute(text("SELECT COUNT(*) FROM knowledge_points"))
            kp_count = result.scalar()
            if kp_count > 0:
                print(f"[Seed] Database exists with {kp_count} knowledge points, skipping.")
                return

            # DB exists but no knowledge_points — check for users before acting
            try:
                result2 = await db.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result2.scalar()
            except Exception:
                user_count = 0

            if user_count > 0:
                print(f"[Seed] DB has {user_count} users but 0 knowledge_points. "
                      f"Importing seed data only (preserving users)...")
                needs_safe_import = True

        # Safe import: use sync sqlite3 outside async session to avoid lock conflicts
        if needs_safe_import:
            await asyncio.to_thread(_safe_import_seed_data, target_db)
            return

        print("[Seed] DB file exists but empty, will re-seed.")

    # Target DB doesn't exist or is completely empty — start fresh from bundled
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

    # Strategy 3: Fallback - run seed scripts (for dev environments)
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
