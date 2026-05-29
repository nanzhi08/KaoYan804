"""将 .doc C语言章节练习转换为文本并解析题目导入题库"""
import sys
sys.path.insert(0, ".")

import asyncio
import hashlib
import os
import re
import subprocess
from pathlib import Path

from sqlalchemy import select
from app.database import async_session, init_db
from app.models.knowledge_point import KnowledgePoint
from app.models.question import Question, QuestionKnowledgePoint

DOC_DIR = Path(r"C:\Users\zhangsihai\Desktop\考研知识库系统\二工大804资料包\c语言各章节练习题")
OUTPUT_DIR = Path(r"C:\Users\zhangsihai\Desktop\考研知识库系统\scripts\doc_converted")

CHAPTER_MAP = {
    "第1章": "1.1", "第2章": "1.1", "第3章": "1.3",
    "第4章": "1.4", "第5章": "1.5", "第6章": "1.6",
    "第7章": "1.4", "第8章": "1.2", "第9章": "1.7",
}


def normalize_content(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", "", text)
    text = text.lower()
    text = text.replace("\uff0c", ",").replace("\u3001", ",")
    text = text.replace("\uff08", "(").replace("\uff09", ")")
    text = text.replace("\uff1a", ":").replace("\uff1b", ";")
    return text


def content_hash(text: str) -> str:
    return hashlib.sha256(normalize_content(text).encode()).hexdigest()


def convert_doc_to_text(doc_path: Path) -> str | None:
    """Get converted text - files already converted by convert_doc_to_txt.py"""
    output_path = OUTPUT_DIR / (doc_path.stem + ".txt")
    if not output_path.exists():
        return None
    raw = output_path.read_bytes()
    # Word COM wdFormatUnicodeText uses system encoding on Chinese Windows (GBK)
    for enc in ["gbk", "gb18030", "utf-16-le", "utf-8"]:
        try:
            text = raw.decode(enc)
            if any("\u4e00" <= ch <= "\u9fff" for ch in text[:500]):
                return text
        except (UnicodeDecodeError, UnicodeError):
            continue
    return raw.decode("gbk", errors="replace")


def parse_questions_from_text(text: str, chapter: str) -> list[dict]:
    """Parse questions from converted C exercise text."""
    questions = []

    # Find exercise sections by looking for numbered questions with options
    # Pattern: number．question text （embedded_answer）\n（A）...\n（B）...\n（C）...\n（D）...

    # Find all question blocks: numbered question followed by options
    q_pattern = re.compile(
        r"(\d+)．\s*(.+?)\s*(?=\n\s*\d+．|\n\s*[一二三四五六七八九十]、|\Z)",
        re.DOTALL
    )

    for qm in q_pattern.finditer(text):
        q_num = qm.group(1)
        q_body = qm.group(2)

        # Find option markers
        opt_markers = list(re.finditer(r"[（\(]([A-D])[）\)]", q_body))
        if len(opt_markers) < 2:
            continue

        # Extract options
        options = {}
        for i, m in enumerate(opt_markers):
            letter = m.group(1)
            start = m.end()
            end = opt_markers[i + 1].start() if i + 1 < len(opt_markers) else len(q_body)
            txt = q_body[start:end].strip()
            txt = re.sub(r"\s*\n\s*", " ", txt)
            options[letter] = txt

        if len(options) < 2:
            continue

        # Remove option text from question content
        q_content = q_body[:opt_markers[0].start()].strip()

        # Extract embedded answer from question content
        # Pattern: （   C  ） or （C） at the end of the question
        ans_m = re.search(r"[（\(]\s*([A-D])\s*[）\)]\s*$", q_content)
        answer = ""
        if ans_m:
            answer = ans_m.group(1)
            q_content = q_content[:ans_m.start()].strip()

        if not q_content or len(q_content) < 5:
            continue

        # Remove leading question number from content
        q_content = re.sub(r"^\d+[．.\s]+", "", q_content).strip()

        questions.append({
            "type": "single_choice" if options else "fill_blank",
            "part": "C_programming",
            "difficulty": 2,
            "content": q_content[:2000],
            "options": options if options else None,
            "answer": answer if answer else "?",
            "explanation": "",
            "source": f"C语言分章练习题-{chapter}",
            "kp_chapter": chapter,
        })

    return questions


async def run_import(dry_run: bool = True):
    await init_db()

    async with async_session() as db:
        result = await db.execute(select(Question))
        existing = result.scalars().all()
        existing_hashes = {content_hash(q.content): q for q in existing}

        kp_result = await db.execute(
            select(KnowledgePoint).where(
                KnowledgePoint.chapter != "",
                KnowledgePoint.parent_id.isnot(None),
                KnowledgePoint.part == "C_programming",
            )
        )
        kps = kp_result.scalars().all()
        kp_by_chapter = {}
        for kp in kps:
            if kp.chapter not in kp_by_chapter:
                kp_by_chapter[kp.chapter] = kp

        total_parsed = 0
        total_new = 0

        for doc_file in sorted(DOC_DIR.glob("*.doc")):
            print(f"\nProcessing: {doc_file.name}")

            text = convert_doc_to_text(doc_file)
            if not text:
                continue

            for cn_name, chapter in CHAPTER_MAP.items():
                if cn_name in doc_file.name:
                    break
            else:
                continue

            kp = kp_by_chapter.get(chapter)
            if not kp:
                print(f"  No KP for chapter {chapter}, skipping")
                continue

            parsed = parse_questions_from_text(text, chapter)
            total_parsed += len(parsed)
            new_for_file = 0

            for q_data in parsed:
                h = content_hash(q_data["content"])
                if h in existing_hashes:
                    continue

                chapter_code = q_data.pop("kp_chapter")
                q_data["knowledge_point_ids"] = [kp.id]
                new_for_file += 1

                if not dry_run:
                    kp_ids = q_data.pop("knowledge_point_ids", [])
                    q = Question(**q_data)
                    db.add(q)
                    await db.flush()
                    for kp_id in kp_ids:
                        db.add(QuestionKnowledgePoint(question_id=q.id, knowledge_point_id=kp_id))

            total_new += new_for_file
            print(f"  Parsed: {len(parsed)}, New: {new_for_file}")

        if not dry_run:
            await db.commit()

        print(f"\n=== Summary ===")
        print(f"Total parsed: {total_parsed}, New to import: {total_new}")
        if dry_run:
            print(f"[DRY RUN] Use --no-dry-run to execute import.")


if __name__ == "__main__":
    dry_run = "--no-dry-run" not in sys.argv
    asyncio.run(run_import(dry_run=dry_run))
