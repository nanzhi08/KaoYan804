"""Fix questions with missing answers (?).

Strategy: Re-extract source PDFs for the worst-affected sources,
parse answer keys, and match answers to questions by sequential order.

Usage:
    PYTHONPATH=backend python scripts/fix_missing_answers.py          # dry-run
    PYTHONPATH=backend python scripts/fix_missing_answers.py --no-dry-run  # apply fixes
"""

import sys
sys.path.insert(0, ".")

import asyncio
import hashlib
import re
from pathlib import Path

import pdfplumber

from app.database import async_session, init_db
from sqlalchemy import select, update
from app.models.question import Question

PACKAGE = Path(r"C:\Users\zhangsihai\Desktop\考研知识库系统\二工大804资料包")

# ============================================================================
# Answer extractors for each source
# ============================================================================


def extract_ds_answers(text: str) -> list[str]:
    """Extract MC answer letters from DS十套卷 text.
    Each exam paper has answers organized by section."""
    letters = []

    # Find all answer sections: "一、单项选择题" followed by answer strings
    ans_sections = re.findall(
        r'(?:一[、.]\s*(?:单项|选择)|[一二三四五六七八九十]+[、.].*?答案).*?((?:\d+[-–]\d+\s*[A-D\s]+)+)',
        text, re.DOTALL
    )

    for section in ans_sections:
        for m in re.finditer(r'(\d+)[-–](\d+)\s*((?:\s*[A-D])+)', section):
            found = re.findall(r'[A-D]', m.group(3))
            letters.extend(found)

    # Also try: standalone "N. A  N. B" patterns near answer sections
    if not letters:
        ans_area = re.search(r'(?:参考答案|答案).*', text, re.DOTALL)
        if ans_area:
            area = ans_area.group()
            letters = re.findall(r'\d+[．、.]\s*([A-D])\b', area)

    return letters


def extract_tiku2_answers(text: str) -> list[str]:
    """Extract MC answer letters from 题库2 answer sections."""
    letters = []

    # Find answer sections with letter ranges
    for m in re.finditer(
        r'(\d+)\s*[-–]\s*(\d+)\s*((?:\s*[A-D])+)',
        text
    ):
        found = re.findall(r'[A-D]+', m.group(3))
        letters.extend(found)

    return letters


def extract_generic_answers(text: str) -> list[str]:
    """Generic answer extractor for various formats."""
    letters = []

    # Pattern: "1．A  2．B  3．C"
    simple = re.findall(r'(?<!\d)(\d+)[．、.)]\s*([A-D])\b', text)
    if simple:
        letters = [l for _, l in simple]
        return letters

    # Pattern: "1-5 A B C D A  6-10 B C D A B"
    for m in re.finditer(r'(\d+)[-–](\d+)\s*((?:\s*[A-D])+)', text):
        found = re.findall(r'[A-D]', m.group(3))
        letters.extend(found)

    return letters


# ============================================================================
# Source-specific answer extraction from PDFs
# ============================================================================

SOURCE_FIXES = {
    "DS十套卷": {
        "pdf": "数据结构10套卷/数据结构十套卷.pdf",
        "extractor": extract_ds_answers,
    },
    "题库2-分章习题集": {
        "pdf": "C语言知识点总结/题库2-C语言分章习题集附答案【50页】.pdf",
        "extractor": extract_tiku2_answers,
    },
}

# ============================================================================
# Main fix logic
# ============================================================================


async def fix_answers(dry_run: bool = True):
    await init_db()

    async with async_session() as db:
        # Get all ? questions
        result = await db.execute(
            select(Question)
            .where(Question.answer == "?")
            .where(Question.options.isnot(None))
            .order_by(Question.source, Question.id)
        )
        bad_questions = result.scalars().all()
        print(f"Questions with ? answer (MC): {len(bad_questions)}")

        # Group by source
        by_source: dict[str, list] = {}
        for q in bad_questions:
            src = q.source or ""
            by_source.setdefault(src, []).append(q)

        total_fixed = 0

        for source, questions in by_source.items():
            print(f"\n--- {source}: {len(questions)} missing ---")

            # Try to get answers from source PDF
            answers_list: list[str] = []

            if source in SOURCE_FIXES:
                fix_info = SOURCE_FIXES[source]
                pdf_path = PACKAGE / fix_info["pdf"]
                if pdf_path.exists():
                    with pdfplumber.open(str(pdf_path)) as pdf:
                        text = "\n".join(p.extract_text() or "" for p in pdf.pages)
                    answers_list = fix_info["extractor"](text)
                    print(f"  Extracted {len(answers_list)} answers from PDF")
            else:
                # Generic extraction from the source name
                answers_list = []

            if not answers_list:
                print(f"  No answers recoverable from PDF")
                continue

            # Match answers to questions sequentially
            fixed = 0
            for i, q in enumerate(questions):
                if i < len(answers_list):
                    new_ans = answers_list[i]
                    if len(new_ans) == 1 and new_ans in "ABCD":
                        if not dry_run:
                            await db.execute(
                                update(Question)
                                .where(Question.id == q.id)
                                .values(answer=new_ans)
                            )
                        fixed += 1

            total_fixed += fixed
            print(f"  Would fix: {fixed}" if dry_run else f"  Fixed: {fixed}")

        if not dry_run:
            await db.commit()
            print(f"\n=== Total fixed: {total_fixed} ===")
        else:
            print(f"\n[DRY RUN] Would fix {total_fixed} questions. Use --no-dry-run to apply.")


if __name__ == "__main__":
    dry_run = "--no-dry-run" not in sys.argv
    asyncio.run(fix_answers(dry_run=dry_run))
