"""OCR + 解析 PDF 题库题目，去重后导入"""
import sys
sys.path.insert(0, ".")

import asyncio
import hashlib
import os
import re
from pathlib import Path

import pdfplumber

from app.database import async_session, init_db
from sqlalchemy import select
from app.models.knowledge_point import KnowledgePoint
from app.models.question import Question, QuestionKnowledgePoint

PACKAGE_DIR = Path(r"C:\Users\zhangsihai\Desktop\考研知识库系统\二工大804资料包")

# Target PDFs: (relative_path, chapter, part)
TARGET_PDFS = [
    # === 真题 (Exam papers) ===
    ("2022-2025真题/2022年上海第二工业大学804真题.pdf", "1.1", "C_programming"),
    ("2022-2025真题/2023年上海第二工业大学804真题.pdf", "1.1", "C_programming"),
    ("2022-2025真题/2024年上海第二工业大学804真题.pdf", "1.1", "C_programming"),
    ("2022-2025真题/25二工大804回忆版.pdf", "1.1", "C_programming"),

    # === C语言题库 (smaller ones first) ===
    ("C语言知识点总结/题库7-C语言程序设计模拟试题及答案【6页】.pdf", "1.1", "C_programming"),
    ("C语言知识点总结/题库8-C语言程序模拟试题【8页】.pdf", "1.1", "C_programming"),
    ("C语言知识点总结/题库9-c语言经典程序题目【12页】.pdf", "1.1", "C_programming"),
    ("C语言知识点总结/题库10-C语言复习题库【18页】.pdf", "1.1", "C_programming"),
    ("C语言知识点总结/题库11-c语言简答题100道附答案.pdf", "1.1", "C_programming"),
    ("C语言知识点总结/题库4-C语言程序改错题库【80页】.pdf", "1.1", "C_programming"),
    ("C语言知识点总结/题库5-大学C语言期末试题与答案【55页】.pdf", "1.1", "C_programming"),
    ("C语言知识点总结/题库6-c语言程序填空题库【28页】.pdf", "1.1", "C_programming"),

    # === Larger C语言题库 ===
    ("C语言知识点总结/题库1-C语言分章习题库附答案【90页】.pdf", "1.1", "C_programming"),
    ("C语言知识点总结/题库2-C语言分章习题集附答案【50页】.pdf", "1.1", "C_programming"),
    ("C语言知识点总结/题库3-c语言10套卷含答案【32页】.pdf", "1.1", "C_programming"),

    # === DS papers ===
    ("数据结构10套卷/数据结构十套卷.pdf", "2.1", "data_structure"),
    ("数据结构校内期末试题/数据结构期末卷.pdf", "2.1", "data_structure"),
    ("数据结构校内期末试题/数据结构期末卷 (2).pdf", "2.1", "data_structure"),
]


def normalize_content(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", "", text)
    text = text.lower()
    text = text.replace("\uff0c", ",").replace("\u3001", ",")
    text = text.replace("\uff08", "(").replace("\uff09", ")")
    text = text.replace("\uff1a", ":").replace("\uff1b", ";")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    return text


def content_hash(text: str) -> str:
    return hashlib.sha256(normalize_content(text).encode()).hexdigest()


def extract_text_from_pdf(pdf_path: Path) -> str | None:
    """Extract text from PDF using pdfplumber. Returns None if no extractable text."""
    try:
        text_parts = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        full_text = "\n".join(text_parts)
        if len(full_text.strip()) < 50:
            return None
        return full_text
    except Exception as e:
        print(f"    pdfplumber error: {e}")
        return None


def parse_questions_from_text(text: str, part: str, default_chapter: str) -> list[dict]:
    """Parse questions from exam/exercise text. Handles various formats."""
    questions = []

    # Split into smaller chunks by blank lines to find question groups
    # Look for numbered questions with option patterns
    # Format 1: N．question （  ） \n A．xxx B．xxx C．xxx D．xxx
    # Format 2: （N）question \n A．xxx \n B．xxx

    # Find all question patterns
    q_starts = list(re.finditer(
        r"(?:^|\n)\s*(?:（\d+）|\d+[．.、]\s*)",
        text, re.MULTILINE
    ))

    for i, start_m in enumerate(q_starts):
        q_start = start_m.start()
        q_end = q_starts[i + 1].start() if i + 1 < len(q_starts) else min(len(text), q_start + 2000)
        q_block = text[q_start:q_end].strip()

        if len(q_block) < 10:
            continue

        # Check if it has options (A/B/C/D markers)
        opt_pattern = re.findall(r"(?:\n|^)\s*([A-D])[．.、]\s*(.+?)(?=\n\s*[A-D][．.、]|\n\n|\Z)", q_block, re.DOTALL)
        has_options = len(opt_pattern) >= 2

        # Extract answer
        answer = ""
        ans_m = re.search(r"(?:答案|正确答案)[：:\s]*([A-D]+)", q_block)
        if not ans_m:
            ans_m = re.search(r"(?:^|\n)\s*[（(]\s*([A-D]+)\s*[）)]\s*(?:\n|$)", q_block)

        if ans_m:
            answer = ans_m.group(1).strip()
        elif has_options:
            # Try to find answer embedded near end
            ans_embedded = re.search(r"[（(]\s*([A-D])\s*[）)]", q_block[-100:])
            if ans_embedded:
                answer = ans_embedded.group(1)

        if not answer and not has_options:
            continue  # Skip: no way to determine answer

        # Extract question content (without options)
        q_content = q_block
        options = {}

        if has_options:
            for letter, opt_text in opt_pattern:
                options[letter] = opt_text.strip()[:500]
            # Remove option lines from content
            first_opt_idx = q_block.find(f"\n{opt_pattern[0][0]}")
            if first_opt_idx > 0:
                q_content = q_block[:first_opt_idx].strip()

        # Clean question content
        q_content = re.sub(r"^\s*(?:（\d+）|\d+[．.、])\s*", "", q_content).strip()
        q_content = re.sub(r"\n{3,}", "\n\n", q_content).strip()

        if len(q_content) < 5:
            continue

        # Determine type
        q_type = "single_choice" if options else "fill_blank"
        if re.search(r"编程|编写程序|写出代码|编程题", q_content[:200]):
            q_type = "programming"
        elif re.search(r"时间复杂度|算法分析|频度", q_content[:200]):
            q_type = "analysis"
        elif re.search(r"程序.?运行.?结果|程序.?输出|写出输出|程序阅读", q_content[:200]):
            q_type = "program_reading"
        elif re.search(r"简答|简述|概念|定义|什么是|说明", q_content[:200]):
            q_type = "short_answer"
        elif re.search(r"计算|求值|等于", q_content[:200]) and not options:
            q_type = "calculation"

        questions.append({
            "type": q_type,
            "part": part,
            "difficulty": 2,
            "content": q_content[:2000],
            "options": options if options else None,
            "answer": answer if answer else "?",
            "explanation": "",
            "source": "PDF题库-OCR",
            "kp_chapter": default_chapter,
        })

    return questions


async def run_ocr_and_import(dry_run: bool = True):
    await init_db()

    async with async_session() as db:
        result = await db.execute(select(Question))
        existing = result.scalars().all()
        existing_hashes = {content_hash(q.content): q for q in existing}

        kp_result = await db.execute(
            select(KnowledgePoint).where(
                KnowledgePoint.chapter != "",
                KnowledgePoint.parent_id.isnot(None),
            )
        )
        kps = kp_result.scalars().all()
        kp_by_key = {}
        for kp in kps:
            key = (kp.part, kp.chapter)
            if key not in kp_by_key:
                kp_by_key[key] = kp

        total_new = 0
        total_parsed = 0

        for rel_path, default_ch, part in TARGET_PDFS:
            pdf_path = PACKAGE_DIR / rel_path
            if not pdf_path.exists():
                print(f"SKIP (not found): {rel_path}")
                continue

            print(f"\nProcessing: {pdf_path.name} ({pdf_path.stat().st_size/1024:.0f}KB)")

            # Try to read text
            text = extract_text_from_pdf(pdf_path)
            if not text:
                print(f"  No extractable text (scanned PDF) - skipping for now")
                continue

            print(f"  Extracted {len(text)} chars of text")

            parsed = parse_questions_from_text(text, part, default_ch)
            total_parsed += len(parsed)
            new = 0

            for q_data in parsed:
                h = content_hash(q_data["content"])
                if h in existing_hashes:
                    continue

                chapter = q_data.pop("kp_chapter")
                kp = kp_by_key.get((q_data["part"], chapter))
                if not kp:
                    kp = kp_by_key.get((q_data["part"], "1.1")) if part == "C_programming" else \
                         kp_by_key.get((q_data["part"], "2.1"))
                if not kp:
                    continue

                new += 1
                if not dry_run:
                    q = Question(**q_data)
                    db.add(q)
                    await db.flush()
                    db.add(QuestionKnowledgePoint(question_id=q.id, knowledge_point_id=kp.id))

            total_new += new
            print(f"  Parsed: {len(parsed)}, New: {new}")

        if not dry_run:
            await db.commit()

        print(f"\n=== Total: parsed {total_parsed}, new {total_new} ===")
        if dry_run:
            print("[DRY RUN] Use --no-dry-run to import.")


if __name__ == "__main__":
    dry_run = "--no-dry-run" not in sys.argv
    asyncio.run(run_ocr_and_import(dry_run=dry_run))
