"""Fix questions with embedded answers in content text.

Pattern: content like "正确的是（  C  ）" has the answer letter
inside Chinese parentheses. We extract the answer and clean the content.

Usage:
    PYTHONPATH=backend python scripts/fix_embedded_answers.py          # dry-run
    PYTHONPATH=backend python scripts/fix_embedded_answers.py --no-dry-run
"""

import sys
sys.path.insert(0, ".")

import asyncio
import re
from app.database import async_session, init_db
from sqlalchemy import select, update
from app.models.question import Question


def extract_embedded(content: str) -> tuple[str | None, str]:
    """Extract answer letter from embedded pattern like （  C  ）.
    Returns (answer_letter, cleaned_content).

    Also handles: （C）、(B)、（  A  ）、（  ABCD  ） for multi-choice.
    """
    # Pattern: Chinese or ASCII parentheses with letter(s) inside
    # Match: （  C  ）、(C)、（ A ）、（ B ）、（ ABCD ）etc.
    m = re.search(r'[（(]\s*([A-Da-d]{1,4})\s*[）)]', content)
    if m:
        answer = m.group(1).upper()
        # Remove the embedded answer from content
        cleaned = content[:m.start()] + content[m.end():]
        # Clean up extra spaces
        cleaned = re.sub(r'\s{2,}', ' ', cleaned).strip()
        # Remove trailing punctuation if orphaned
        cleaned = re.sub(r'[，,。；;]\s*$', '', cleaned).strip()
        return answer, cleaned
    return None, content


async def fix_embedded(dry_run: bool = True):
    await init_db()

    async with async_session() as db:
        result = await db.execute(
            select(Question).where(Question.answer == "?")
        )
        bad_questions = result.scalars().all()
        print(f"Questions with ? answer: {len(bad_questions)}")

        fixed = 0
        for q in bad_questions:
            answer, cleaned = extract_embedded(q.content)
            if answer and len(answer) <= 4:
                if not dry_run:
                    await db.execute(
                        update(Question)
                        .where(Question.id == q.id)
                        .values(answer=answer, content=cleaned)
                    )
                fixed += 1
                if fixed <= 10:
                    print(f"  ID={q.id}: '{q.content[:50]}...' -> ans={answer}")

        if not dry_run:
            await db.commit()
            print(f"\n=== Fixed: {fixed} questions ===")
        else:
            print(f"\n[DRY RUN] Would fix {fixed} questions. Use --no-dry-run to apply.")


if __name__ == "__main__":
    dry_run = "--no-dry-run" not in sys.argv
    asyncio.run(fix_embedded(dry_run=dry_run))
