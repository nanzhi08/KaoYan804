"""Fix stuck options where A+B or C+D are merged into one value.

Example: {"A": "0L B.-0x6aL", "C": "'6' D. 1.234E3.5"}
Should be: {"A":"0L", "B":"-0x6aL", "C":"'6'", "D":"1.234E3.5"}

Usage:
    PYTHONPATH=backend python scripts/fix_sticky_options.py          # dry-run
    PYTHONPATH=backend python scripts/fix_sticky_options.py --no-dry-run
"""

import sys
sys.path.insert(0, ".")

import asyncio
import re
import json
from app.database import async_session, init_db
from sqlalchemy import select, update
from app.models.question import Question


def split_stuck_options(options: dict) -> dict | None:
    """If options has stuck pairs, split them. Returns fixed dict or None."""
    if not options or len(options) >= 4:
        return None

    fixed = dict(options)
    changed = False

    # Pattern: "xxx B. yyy" or "xxx B) yyy" in value
    stuck_pattern = re.compile(r'\s+([B-D])[.、．)）]\s*')

    for key in list(fixed.keys()):
        val = fixed[key]
        m = stuck_pattern.search(val)
        if m:
            next_key = m.group(1)
            split_pos = m.start()
            fixed[key] = val[:split_pos].strip()
            fixed[next_key] = val[split_pos:].strip()
            # Remove the next_key's label prefix
            fixed[next_key] = re.sub(r'^[B-D][.、．)）]\s*', '', fixed[next_key]).strip()
            changed = True

    return fixed if changed else None


async def fix_sticky(dry_run: bool = True):
    await init_db()

    async with async_session() as db:
        result = await db.execute(
            select(Question).where(Question.options.isnot(None))
        )
        questions = result.scalars().all()

        fixed_count = 0
        for q in questions:
            try:
                opts = q.options
                if isinstance(opts, str):
                    opts = json.loads(opts)
                if not isinstance(opts, dict) or len(opts) >= 4:
                    continue
            except (json.JSONDecodeError, TypeError):
                continue

            fixed = split_stuck_options(opts)
            if fixed:
                if not dry_run:
                    await db.execute(
                        update(Question)
                        .where(Question.id == q.id)
                        .values(options=fixed)
                    )
                fixed_count += 1
                if fixed_count <= 5:
                    print(f"  ID={q.id}: {json.dumps(opts, ensure_ascii=False)}")
                    print(f"    -> {json.dumps(fixed, ensure_ascii=False)}")

        if not dry_run:
            await db.commit()
            print(f"\n=== Fixed: {fixed_count} questions ===")
        else:
            print(f"\n[DRY RUN] Would fix {fixed_count} questions. Use --no-dry-run to apply.")


if __name__ == "__main__":
    dry_run = "--no-dry-run" not in sys.argv
    asyncio.run(fix_sticky(dry_run=dry_run))
