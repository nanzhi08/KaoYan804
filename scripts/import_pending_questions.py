"""Unified import script for all pending PDFs.

Handles:
  - Text-extracted PDFs: 题库2, 题库7, 题库9, 题库11
  - Pre-extracted text: 2025回忆版
  - OCR output: 2022真题, 2023真题, 题库3-10套卷, 题库6-程序填空

Usage:
    PYTHONPATH=backend python scripts/import_pending_questions.py           # dry-run
    PYTHONPATH=backend python scripts/import_pending_questions.py --no-dry-run
    PYTHONPATH=backend python scripts/import_pending_questions.py --source=题库11  # single source
"""

import sys
sys.path.insert(0, ".")

import asyncio
import hashlib
import re
from pathlib import Path

import pdfplumber

from app.database import async_session, init_db
from sqlalchemy import select
from app.models.knowledge_point import KnowledgePoint
from app.models.question import Question, QuestionKnowledgePoint

PACKAGE_DIR = Path(r"C:\Users\zhangsihai\Desktop\考研知识库系统\二工大804资料包")
OCR_OUTPUT_DIR = Path(__file__).parent / "ocr_output"

# Chapter mapping: 第X章 text -> chapter code
C_CHAPTER_MAP = {
    "第1章": "1.1", "第一章": "1.1",
    "第2章": "1.2", "第二章": "1.2",
    "第3章": "1.3", "第三章": "1.3",
    "第4章": "1.4", "第四章": "1.4",
    "第5章": "1.5", "第五章": "1.5",
    "第6章": "1.6", "第六章": "1.6",
    "第7章": "1.7", "第七章": "1.7",
    "第8章": "1.2", "第八章": "1.2",  # 位运算 → ch1.2
    "第9章": "1.7", "第九章": "1.7",  # 文件 → ch1.7
}


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


def extract_text_from_pdf(pdf_path: Path) -> str:
    with pdfplumber.open(str(pdf_path)) as pdf:
        texts = []
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                texts.append(t)
        return "\n".join(texts)


def determine_type(content: str, has_options: bool, answer: str = "") -> str:
    """Infer question type from content keywords."""
    if re.search(r"编程|编写程序|写出代码|编程题", content[:200]):
        return "programming"
    if re.search(r"时间复杂度|算法分析|频度", content[:200]):
        return "analysis"
    if re.search(r"程序.?运行.?结果|程序.?输出|写出输出|程序阅读|读程序", content[:200]):
        return "program_reading"
    if re.search(r"简答|简述|概念|定义|什么是|说明|解释", content[:200]):
        return "short_answer"
    if re.search(r"计算|求值|等于", content[:200]) and not has_options:
        return "calculation"
    if has_options:
        return "single_choice"
    return "fill_blank"


# ============================================================================
# Parser: 题库2 - 分章习题集 (50 pages)
# Format: Chapter → Section → Numbered questions with A/B/C/D options
# Answers: At end of each chapter, e.g., "1-5 B B B A C  6-10 D A C B B"
# ============================================================================

def parse_tiku2(text: str) -> list[dict]:
    """Parse 题库2-C语言分章习题集.

    The PDF has 50 pages. First ~30 pages are question sections, last ~20
    pages are answer keys. Answers appear in two batches: first batch has
    fill-blank/program-reading answers (no letters), second batch has MC
    answers with explicit letters like "1-5 C B B B C".
    """
    questions = []

    all_headers = list(re.finditer(r'一\s+单项选择', text))

    # Classify headers
    q_headers = []
    a_letter_headers = []
    for h in all_headers:
        after = text[h.end():h.end()+300]
        if re.search(r'\d+[-–]\d+\s*[A-D]', after):
            a_letter_headers.append(h)
        elif not re.search(r'\d+[-–]\d+', after):
            q_headers.append(h)

    # --- Extract MC answer letters from letter answer sections ---
    ans_letters = []
    for h in a_letter_headers:
        section = text[h.end():h.end()+2000]
        # Extract answer ranges with letters: "1-5 C B B B C"
        for range_m in re.finditer(
            r'(\d+)\s*[-–]\s*(\d+)\s*((?:\s*[A-D]+)+)',
            section
        ):
            tail = range_m.group(3)
            letters = re.findall(r'[A-D]+', tail)
            ans_letters.extend(letters)

    # --- Parse questions ---
    mc_idx = 0

    for h in q_headers:
        # Find the bounds of this question section
        next_h = None
        for h2 in all_headers:
            if h2.start() > h.start():
                next_h = h2
                break
        section_end = next_h.start() if next_h else len(text)
        section = text[h.end():section_end]

        # Find numbered question starts
        q_starts = list(re.finditer(
            r'(?:^|\n)\s*(\d+)\s+(?=[A-Z\u4e00-\u9fff])',
            section, re.MULTILINE
        ))

        for i, m in enumerate(q_starts):
            q_start = m.end()
            q_end = q_starts[i + 1].start() if i + 1 < len(q_starts) else len(section)
            q_block = section[q_start:q_end].strip()

            if len(q_block) < 5:
                continue

            # Extract options (A/B/C/D followed by text)
            opt_matches = list(re.finditer(
                r'(?:^|\n)\s*([A-D])\s+([^\n]+)',
                q_block, re.MULTILINE
            ))
            options = {}
            q_content = q_block

            if len(opt_matches) >= 2:
                for om in opt_matches:
                    options[om.group(1)] = om.group(2).strip()[:500]
                first_opt_pos = opt_matches[0].start()
                if first_opt_pos > 0:
                    q_content = q_block[:first_opt_pos].strip()

            has_options = len(options) >= 2

            # Get answer by sequential index for MC questions
            answer = ""
            if has_options and mc_idx < len(ans_letters):
                answer = ans_letters[mc_idx]
                mc_idx += 1
            elif has_options:
                mc_idx += 1  # still advance the index

            if not has_options and not answer:
                # Non-MC questions without answers - still include them
                pass

            q_content_clean = q_content.strip()[:2000]
            q_type = determine_type(q_content_clean, has_options, answer)

            questions.append({
                "type": q_type,
                "part": "C_programming",
                "difficulty": 2,
                "content": q_content_clean,
                "options": options if options else None,
                "answer": answer if answer else "?",
                "explanation": "",
                "source": "题库2-分章习题集",
                "kp_chapter": "1.1",
            })

    return questions


# ============================================================================
# Parser: 题库7 - 模拟试题 (6 pages)
# Format: Traditional exam paper, answers embedded in questions
# ============================================================================

def parse_tiku7(text: str) -> list[dict]:
    """Parse 题库7-C语言模拟试题."""
    questions = []

    # Split by section headers
    sections = re.split(
        r'\n(?=[一二三四五六七八九十]、\s*(?:单项选择|填空|程序|编程|简答|判断|选择))',
        text
    )

    for section in sections:
        section_type = "single_choice"
        if re.search(r'填空', section[:50]):
            section_type = "fill_blank"
        elif re.search(r'程序|编程', section[:50]):
            section_type = "programming"

        # Find numbered questions
        q_pattern = re.compile(
            r'(?:^|\n)\s*(\d+)[．、.)]\s*(.+?)(?=\n\s*\d+[．、.)]\s*|\n\s*[一二三四五六七八九十]、|\Z)',
            re.DOTALL
        )

        for m in q_pattern.finditer(section):
            q_block = m.group(2).strip()
            if len(q_block) < 5:
                continue

            # Extract inline answer: （B） or (B) near beginning or end
            answer = ""
            ans_m = re.search(r'[（(]\s*([A-D]+)\s*[）)]', q_block[:100])
            if not ans_m:
                ans_m = re.search(r'[（(]\s*([A-D]+)\s*[）)]', q_block[-100:])
            if ans_m:
                answer = ans_m.group(1)
                # Remove answer marker from content
                q_block = q_block.replace(ans_m.group(0), "").strip()

            # For fill-blank, look for ___ markers
            if section_type == "fill_blank":
                # Answer might be embedded separately
                ans_fill = re.findall(r'[（(]\s*([^）)]+?)\s*[）)]', q_block)
                if ans_fill and not answer:
                    answer = "||".join(ans_fill)

            # Extract options
            opt_pattern = re.findall(
                r'(?:^|\n)\s*([A-D])\s*[)）．、.\s]\s*(.+?)(?=\n\s*[A-D]\s*[)）．、.\s]|\Z)',
                q_block, re.DOTALL
            )
            options = {}
            q_content = q_block

            if len(opt_pattern) >= 2:
                for letter, opt_text in opt_pattern:
                    options[letter] = opt_text.strip()[:500]
                first_opt = q_block.find(f"\n{opt_pattern[0][0]}")
                if first_opt < 0:
                    first_opt = q_block.find(f"{opt_pattern[0][0]})")
                if first_opt > 0:
                    q_content = q_block[:first_opt].strip()

            if len(q_content) < 5:
                continue
            if not answer and not options:
                continue

            q_content_clean = q_content.strip()[:2000]
            q_type = determine_type(q_content_clean, len(options) >= 2, answer)
            if q_type == "single_choice" and section_type == "fill_blank":
                q_type = "fill_blank"

            questions.append({
                "type": q_type,
                "part": "C_programming",
                "difficulty": 2,
                "content": q_content_clean,
                "options": options if options else None,
                "answer": answer if answer else "?",
                "explanation": "",
                "source": "题库7-模拟试题",
                "kp_chapter": "1.1",
            })

    return questions


# ============================================================================
# Parser: 题库9 - 经典程序题目 (12 pages)
# Format: Chinese-numbered code examples, no traditional Q&A structure
# ============================================================================

def parse_tiku9(text: str) -> list[dict]:
    """Parse 题库9-经典程序题目 as programming questions."""
    questions = []

    # Remove watermark text
    text = re.sub(r'微信公众号[：:]\s*研途可跨[^\n]*', '', text)
    text = re.sub(r'更多.*资源.*\n?', '', text)
    text = re.sub(r'版权.*为原作者.*\n?', '', text)

    # Split by Chinese numeral labels
    blocks = re.split(r'\n(?=[一二三四五六七八九十]+[、，．])', text)

    for block in blocks:
        # Extract title
        title_m = re.match(r'([一二三四五六七八九十]+)[、，．]\s*(.+?)(?=\n\s*#include|\n\s*void|\n\s*int\s+main|\Z)', block, re.DOTALL)
        if not title_m:
            continue
        title = title_m.group(2).strip()

        # Extract code
        code_m = re.search(r'(#include.+|void\s+main.+|int\s+main.+)', block, re.DOTALL)
        if not code_m:
            continue
        code = code_m.group(0).strip()[:3000]

        if len(code) < 20:
            continue

        questions.append({
            "type": "programming",
            "part": "C_programming",
            "difficulty": 2,
            "content": f"阅读以下程序，分析其功能：{title}" if title else "阅读以下程序，分析其功能",
            "options": None,
            "answer": "见代码分析",
            "explanation": "",
            "source": "题库9-经典程序题目",
            "code_snippet": code,
            "kp_chapter": "1.1",
        })

    return questions


# ============================================================================
# Parser: 题库11 - 简答题100道 (10 pages)
# Format: N. question \n 答：answer
# ============================================================================

def parse_tiku11(text: str) -> list[dict]:
    """Parse 题库11-简答题100道."""
    questions = []

    # Split by numbered questions
    q_blocks = re.split(r'\n(?=\d+[\.、．]\s*\S)', text)

    for block in q_blocks:
        # Remove number prefix
        block = re.sub(r'^\d+[\.、．]\s*', '', block).strip()
        if len(block) < 10:
            continue

        # Split question and answer
        # pdfplumber extracts "答" as bullet U+25CF ●, also try normal "答："
        parts = re.split(r'\n\s*[●答][：:\s]*', block, maxsplit=1)
        if len(parts) != 2:
            continue

        question_text = parts[0].strip()
        answer_text = parts[1].strip()

        # Clean up code markers
        question_text = re.sub(r'```c?\n?(.+?)```', r'\1', question_text, flags=re.DOTALL)
        answer_text = re.sub(r'```c?\n?(.+?)```', r'\1', answer_text, flags=re.DOTALL)

        if len(question_text) < 5:
            continue

        questions.append({
            "type": "short_answer",
            "part": "C_programming",
            "difficulty": 2,
            "content": question_text[:2000],
            "options": None,
            "answer": answer_text[:2000] if answer_text else "?",
            "explanation": "",
            "source": "题库11-简答题100道",
            "kp_chapter": "1.1",
        })

    return questions


# ============================================================================
# Parser: 真题 (通用) - for OCR output and 2025回忆版
# ============================================================================

def parse_exam_text(text: str, source_label: str) -> list[dict]:
    """Generic parser for exam paper text."""
    questions = []

    # Clean up OCR artifacts
    text = re.sub(r'--- Page \d+ ---', '', text)
    text = re.sub(r'\n{4,}', '\n\n\n', text)

    # Find all numbered question starts
    q_starts = list(re.finditer(
        r'(?:^|\n)\s*(?:（\d+）|(\d+)[．、.）]\s*)',
        text, re.MULTILINE
    ))

    for i, m in enumerate(q_starts):
        q_start = m.end()
        q_end = q_starts[i + 1].start() if i + 1 < len(q_starts) else min(len(text), q_start + 3000)
        q_block = text[q_start:q_end].strip()

        if len(q_block) < 10:
            continue

        # Extract inline answer
        answer = ""
        ans_m = re.search(r'[（(]\s*([A-D]+)\s*[）)]', q_block[:100])
        if not ans_m:
            ans_m = re.search(r'[（(]\s*([A-D]+)\s*[）)]', q_block[-100:])
        if ans_m:
            answer = ans_m.group(1)

        # Extract options
        opt_pattern = re.findall(
            r'(?:^|\n)\s*([A-D])\s*[)）．、.]\s*(.+?)(?=\n\s*[A-D]\s*[)）．、.]|\n\n|\Z)',
            q_block, re.DOTALL
        )
        options = {}
        q_content = q_block

        if len(opt_pattern) >= 2:
            for letter, opt_text in opt_pattern:
                options[letter] = opt_text.strip()[:500]
            first_opt = q_block.find(f"\n{opt_pattern[0][0]}")
            if first_opt < 0:
                first_opt = q_block.find(f"{opt_pattern[0][0]})")
            if first_opt > 0:
                q_content = q_block[:first_opt].strip()

        if len(q_content) < 5:
            continue

        q_content_clean = q_content.strip()[:2000]
        q_type = determine_type(q_content_clean, len(options) >= 2, answer)

        if not answer and not options:
            # Try to detect fill-blank or short-answer
            if re.search(r'[（(]\s*[）)]|___|____|填空', q_content_clean):
                q_type = "fill_blank"
                answer = "?"
            else:
                continue

        questions.append({
            "type": q_type,
            "part": "C_programming",
            "difficulty": 3,
            "content": q_content_clean,
            "options": options if options else None,
            "answer": answer if answer else "?",
            "explanation": "",
            "source": source_label,
            "kp_chapter": "1.1",
        })

    return questions


# ============================================================================
# Output parsed questions summary
# ============================================================================

def print_questions_summary(questions: list[dict], label: str):
    type_counts = {}
    for q in questions:
        t = q["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    print(f"\n  [{label}] Total: {len(questions)}")
    for t, c in sorted(type_counts.items()):
        print(f"    {t}: {c}")


# ============================================================================
# Main async import function
# ============================================================================

ASYNC_HELPER_SCRIPT = """
import asyncio
import hashlib
import re
from pathlib import Path
import pdfplumber
import sys
sys.path.insert(0, ".")

from app.database import async_session, init_db
from sqlalchemy import select
from app.models.knowledge_point import KnowledgePoint
from app.models.question import Question, QuestionKnowledgePoint
"""


# ============================================================================
# Parser: 题库1 - C语言分章习题库 (90 pages)
# Format: Units → standard MC/fill-blank questions → answers at end
# ============================================================================

def parse_tiku1(text: str) -> list[dict]:
    """Parse 题库1-C语言分章习题库附答案."""
    questions = []
    text = re.sub(r'微信公众号[：:].+', '', text)

    # Split into answer part and question part
    ans_header = re.search(r'\n[一二三四五六七八九]+[、.]\s*(?:参考|答案|参考答)', text)
    if ans_header:
        q_text = text[:ans_header.start()]
        a_text = text[ans_header.start():]
    else:
        # No explicit answer header: use last 25% of text as answers
        split = int(len(text) * 0.75)
        q_text = text[:split]
        a_text = text[split:]

    # Parse answers: "1．A" or "1． 顺序结构"
    answer_map = {}
    for m in re.finditer(r'(?:^|\n)\s*(\d+)[．、.]\s*([A-D]+|\S.*?)(?=\n\s*\d+[．、.]|\Z)', a_text, re.DOTALL):
        val = m.group(2).strip()
        if len(val) <= 100:
            qn = int(m.group(1))
            if qn not in answer_map:
                answer_map[qn] = val

    # Parse questions: numbered items
    q_starts = list(re.finditer(r'(?:^|\n)\s*(\d+)[．、.]\s+', q_text, re.MULTILINE))

    for i, m in enumerate(q_starts):
        q_num = int(m.group(1))
        q_start = m.end()
        q_end = q_starts[i + 1].start() if i + 1 < len(q_starts) else len(q_text)
        q_block = q_text[q_start:q_end].strip()
        if len(q_block) < 5:
            continue

        # Extract options
        opt_matches = re.findall(r'(?:^|\n)\s*([A-D])[)）．、.]\s*(.+?)(?=\n\s*[A-D][)）．、.]|\Z)', q_block, re.DOTALL)
        options = {}
        q_content = q_block
        if len(opt_matches) >= 2:
            for letter, opt_text in opt_matches:
                options[letter] = opt_text.strip()[:500]
            first_m = re.search(rf'\n{opt_matches[0][0]}[)）]', q_block)
            if first_m:
                q_content = q_block[:first_m.start()].strip()

        answer = answer_map.get(q_num, "")
        has_opts = len(options) >= 2

        if not answer and not has_opts:
            continue

        q_type = determine_type(q_content[:200], has_opts, answer)
        questions.append({
            "type": q_type, "part": "C_programming", "difficulty": 2,
            "content": q_content.strip()[:2000],
            "options": options if options else None,
            "answer": answer if answer else "?", "explanation": "",
            "source": "题库1-分章习题库", "kp_chapter": "1.1",
        })

    return questions


# ============================================================================
# Parser: 题库5 - 大学C语言期末试题 (55 pages)
# Format: Standard exam with explanations between questions
# ============================================================================

def parse_tiku5(text: str) -> list[dict]:
    """Parse 题库5-大学C语言期末试题与答案."""
    questions = []
    text = re.sub(r'微信公众号[：:].+', '', text)

    # Split by section
    sections = re.split(r'\n(?=[一二三四五六七八九十]+[、.]\s*(?:单项|选择|填空|判断|程序|编程|简答))', text)

    for section in sections:
        # Find numbered questions
        q_starts = list(re.finditer(
            r'(?:^|\n)\s*(\d+)[．、.)]\s*(.+?)(?=\n\s*\d+[．、.)]\s|\n\s*[一二三四五六七八九十]+[、.]|\Z)',
            section, re.DOTALL
        ))

        for m in q_starts:
            q_block = m.group(2).strip()
            if len(q_block) < 5:
                continue

            # Answer often embedded: （ A ）or （B）
            answer = ""
            ans_m = re.search(r'[（(]\s*([A-D]+)\s*[）)]', q_block[:100])
            if ans_m:
                answer = ans_m.group(1)
                q_block = q_block.replace(ans_m.group(0), '', 1).strip()

            # Options: A) xxx B) xxx or A. xxx B. xxx
            opt_matches = re.findall(
                r'(?:^|\n)\s*([A-D])\s*[)）．、.]\s*(.+?)(?=\n\s*[A-D]\s*[)）．、.]|\n\d|\n[一二三四]|\Z)',
                q_block, re.DOTALL
            )
            options = {}
            q_content = q_block
            if len(opt_matches) >= 2:
                for letter, opt_text in opt_matches:
                    options[letter] = opt_text.strip()[:500]
                first_m = re.search(rf'\n{opt_matches[0][0]}[)）]', q_block)
                if first_m:
                    q_content = q_block[:first_m.start()].strip()

            # Skip explanation blocks (they contain "考点：" etc.)
            if re.search(r'考点[：:]|解析[：:]|知识点[：:]', q_content[:100]):
                continue

            has_opts = len(options) >= 2
            if len(q_content) < 5:
                continue
            if not answer and not has_opts:
                continue

            q_type = determine_type(q_content[:200], has_opts, answer)
            questions.append({
                "type": q_type, "part": "C_programming", "difficulty": 2,
                "content": q_content.strip()[:2000],
                "options": options if options else None,
                "answer": answer if answer else "?", "explanation": "",
                "source": "题库5-期末试题", "kp_chapter": "1.1",
            })

    return questions


# ============================================================================
# Parser: 题库8 + 题库10 - 模拟试题/复习题库
# Format: Standard exam, answers at end
# ============================================================================

def parse_tiku8_10(text: str, source: str) -> list[dict]:
    """Parse 题库8/10 - standard exam format with answers at end."""
    questions = []

    # Find answer section
    ans_section = re.search(
        r'\n(?:[一二三四五六七八九十]+[、.]\s*(?:参考|正确)?答案|(?:参考|正确)?答案\s*[：:]?)',
        text
    )
    q_text = text[:ans_section.start()] if ans_section else text
    a_text = text[ans_section.start():] if ans_section else ""

    # Parse answer letters from answer section
    ans_letters = []
    for m in re.finditer(r'(?:(?:^|\n)\s*\d+[．、.\s]+([A-D])\b)|(?:([A-D])\s*[.、])', a_text):
        ans_letters.append(m.group(1) or m.group(2))

    # Parse answer text for non-MC questions
    text_answers = {}
    for m in re.finditer(r'(?:^|\n)\s*(\d+)[．、.\s]+(.+?)(?=\n\s*\d+[．、.]|\Z)', a_text, re.DOTALL):
        val = m.group(2).strip()
        if val and len(val) < 200:
            text_answers[int(m.group(1))] = val

    # Parse questions
    sections = re.split(r'\n(?=[一二三四五六七八九十]+[、.])', q_text)
    mc_idx = 0

    for section in sections:
        q_starts = list(re.finditer(
            r'(?:^|\n)\s*(\d+)[．、.)]\s*(.+?)(?=\n\s*\d+[．、.)]\s|\n\s*[一二三四五六七八九十]+[、.]|\Z)',
            section, re.DOTALL
        ))

        for m in q_starts:
            q_num = int(m.group(1))
            q_block = m.group(2).strip()
            if len(q_block) < 3:
                continue

            opt_matches = re.findall(
                r'(?:^|\n)\s*([A-D])[)）．、.\s]\s*(.+?)(?=\n\s*[A-D][)）．、.\s]|\Z)',
                q_block, re.DOTALL
            )
            options = {}
            q_content = q_block
            if len(opt_matches) >= 2:
                for letter, opt_text in opt_matches:
                    options[letter] = opt_text.strip()[:500]
                first_m = re.search(rf'\n{opt_matches[0][0]}', q_block)
                if first_m:
                    q_content = q_block[:first_m.start()].strip()

            has_opts = len(options) >= 2
            answer = ""
            if has_opts and mc_idx < len(ans_letters):
                answer = ans_letters[mc_idx]
                mc_idx += 1
            elif has_opts:
                mc_idx += 1
            elif q_num in text_answers:
                answer = text_answers[q_num]

            if len(q_content) < 3:
                continue

            q_type = determine_type(q_content[:200], has_opts, answer)
            questions.append({
                "type": q_type, "part": "C_programming", "difficulty": 2,
                "content": q_content.strip()[:2000],
                "options": options if options else None,
                "answer": answer if answer else "?", "explanation": "",
                "source": source, "kp_chapter": "1.1",
            })

    return questions


# ============================================================================
# Parser: DS十套卷 + DS期末卷 + 2024真题
# Format: Data structure exam papers
# ============================================================================

def parse_ds_paper(text: str, source: str) -> list[dict]:
    """Parse DS exam papers (十套卷, 期末卷, 真题)."""
    questions = []

    # Find numbered questions
    q_starts = list(re.finditer(
        r'(?:^|\n)\s*(\d+)[．、.)]\s*',
        text, re.MULTILINE
    ))

    for i, m in enumerate(q_starts):
        q_start = m.end()
        q_end = q_starts[i + 1].start() if i + 1 < len(q_starts) else min(len(text), q_start + 3000)
        q_block = text[q_start:q_end].strip()
        if len(q_block) < 5:
            continue

        # Answer inline
        answer = ""
        ans_m = re.search(r'[（(]\s*([A-D]+)\s*[）)]', q_block[:100])
        if ans_m:
            answer = ans_m.group(1)

        # Options
        opt_matches = re.findall(
            r'(?:^|\n)\s*([A-D])[)）．、.]\s*(.+?)(?=\n\s*[A-D][)）．、.]|\n\n|\Z)',
            q_block, re.DOTALL
        )
        options = {}
        q_content = q_block
        if len(opt_matches) >= 2:
            for letter, opt_text in opt_matches:
                options[letter] = opt_text.strip()[:500]
            first_m = re.search(rf'\n{opt_matches[0][0]}', q_block)
            if first_m:
                q_content = q_block[:first_m.start()].strip()

        has_opts = len(options) >= 2
        q_content_clean = q_content.strip()
        if len(q_content_clean) < 5:
            continue

        # Check if this is really a question (not a section header or narrative)
        if re.match(r'^[一二三四五六七八九十]+[、.]', q_content_clean):
            continue

        q_type = determine_type(q_content_clean[:200], has_opts, answer)
        part = "data_structure" if "DS" in source or "数据" in source else "C_programming"

        questions.append({
            "type": q_type, "part": part, "difficulty": 3,
            "content": q_content_clean[:2000],
            "options": options if options else None,
            "answer": answer if answer else "?", "explanation": "",
            "source": source, "kp_chapter": "2.1" if part == "data_structure" else "1.1",
        })

    return questions


# ============================================================================
# Unified import entry
# ============================================================================

def get_parsed_questions(source_filter: str = None) -> dict[str, list[dict]]:
    """Extract and parse all sources. Returns {source_label: [questions]}."""
    PACKAGE = Path(r"C:\Users\zhangsihai\Desktop\考研知识库系统\二工大804资料包")
    OCR_DIR = Path(r"C:\Users\zhangsihai\Desktop\考研知识库系统\scripts\ocr_output")

    sources = {}

    # --- Text-extracted PDFs ---
    pdf_sources = {
        # Already imported but kept for reference
        "题库2-分章习题集": (PACKAGE / "C语言知识点总结/题库2-C语言分章习题集附答案【50页】.pdf", parse_tiku2),
        "题库7-模拟试题": (PACKAGE / "C语言知识点总结/题库7-C语言程序设计模拟试题及答案【6页】.pdf", parse_tiku7),
        "题库9-经典程序题目": (PACKAGE / "C语言知识点总结/题库9-c语言经典程序题目【12页】.pdf", parse_tiku9),
        "题库11-简答题100道": (PACKAGE / "C语言知识点总结/题库11-c语言简答题100道附答案.pdf", parse_tiku11),
        # New: remaining C language PDFs
        "题库1-分章习题库": (PACKAGE / "C语言知识点总结/题库1-C语言分章习题库附答案【90页】.pdf", parse_tiku1),
        "题库5-期末试题": (PACKAGE / "C语言知识点总结/题库5-大学C语言期末试题与答案【55页】.pdf", parse_tiku5),
        "题库8-程序模拟试题": (PACKAGE / "C语言知识点总结/题库8-C语言程序模拟试题【8页】.pdf",
         lambda t: parse_tiku8_10(t, "题库8-程序模拟试题")),
        "题库10-复习题库": (PACKAGE / "C语言知识点总结/题库10-C语言复习题库【18页】.pdf",
         lambda t: parse_tiku8_10(t, "题库10-复习题库")),
    }

    for label, (pdf_path, parser) in pdf_sources.items():
        if source_filter and source_filter not in label:
            continue
        if not pdf_path.exists():
            print(f"SKIP (not found): {pdf_path}")
            continue
        print(f"Extracting: {label}...", end=" ", flush=True)
        text = extract_text_from_pdf(pdf_path)
        print(f"{len(text)} chars", flush=True)
        sources[label] = parser(text)

    # --- DS exam papers ---
    ds_papers = {
        "DS十套卷": "数据结构10套卷/数据结构十套卷.pdf",
        "DS期末卷": "数据结构校内期末试题/数据结构期末卷.pdf",
        "DS期末卷2": "数据结构校内期末试题/数据结构期末卷 (2).pdf",
    }
    for label, rel_path in ds_papers.items():
        if source_filter and source_filter not in label:
            continue
        path = PACKAGE / rel_path
        if not path.exists():
            print(f"SKIP (not found): {path}")
            continue
        print(f"Extracting: {label}...", end=" ", flush=True)
        text = extract_text_from_pdf(path)
        print(f"{len(text)} chars", flush=True)
        sources[label] = parse_ds_paper(text, label)

    # --- 2024真题 ---
    if not source_filter or "2024" in source_filter:
        path_2024 = PACKAGE / "2022-2025真题/2024年上海第二工业大学804真题.pdf"
        if path_2024.exists():
            print(f"Extracting: 2024真题...", end=" ", flush=True)
            text = extract_text_from_pdf(path_2024)
            print(f"{len(text)} chars", flush=True)
            sources["2024真题"] = parse_ds_paper(text, "2024真题")

    # --- Pre-extracted 2025回忆版 ---
    if not source_filter or "2025" in source_filter:
        txt_path = OCR_DIR / "2025回忆版.txt"
        if txt_path.exists():
            print(f"Reading: 2025回忆版...", end=" ", flush=True)
            text = txt_path.read_text(encoding="utf-8")
            print(f"{len(text)} chars", flush=True)
            sources["2025回忆版"] = parse_exam_text(text, "2025回忆版")

    # --- OCR output files ---
    ocr_files = {
        "2022真题": "2022真题.txt",
        "2023真题": "2023真题.txt",
        "题库3-10套卷": "题库3-10套卷.txt",
        "题库6-程序填空": "题库6-程序填空.txt",
    }
    for label, filename in ocr_files.items():
        if source_filter and source_filter not in label and source_filter not in filename:
            continue
        txt_path = OCR_DIR / filename
        if not txt_path.exists():
            print(f"SKIP (OCR not done): {label}")
            continue
        print(f"Reading: {label}...", end=" ", flush=True)
        text = txt_path.read_text(encoding="utf-8")
        print(f"{len(text)} chars", flush=True)
        sources[label] = parse_exam_text(text, label)

    return sources


async def run_import(dry_run: bool = True, source_filter: str = None):
    await init_db()

    sources = get_parsed_questions(source_filter)
    if not sources:
        print("No sources found to process.")
        return

    async with async_session() as db:
        result = await db.execute(select(Question))
        existing = result.scalars().all()
        existing_hashes = {content_hash(q.content): q for q in existing}
        print(f"\nExisting questions in DB: {len(existing)}")

        # Build KP lookup
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
        total_skipped_dup = 0

        for label, questions in sources.items():
            print_questions_summary(questions, label)
            new = 0
            dup = 0

            for q_data in questions:
                h = content_hash(q_data["content"])
                if h in existing_hashes:
                    dup += 1
                    continue

                chapter = q_data.pop("kp_chapter", "1.1")
                code_snippet = q_data.pop("code_snippet", None)
                kp = kp_by_key.get((q_data["part"], chapter))
                if not kp:
                    kp = kp_by_key.get((q_data["part"], "1.1"))
                if not kp:
                    continue

                new += 1
                if not dry_run:
                    q = Question(**q_data)
                    if code_snippet:
                        q.code_snippet = code_snippet
                    db.add(q)
                    await db.flush()
                    db.add(QuestionKnowledgePoint(question_id=q.id, knowledge_point_id=kp.id))
                    existing_hashes[h] = q

            total_new += new
            total_skipped_dup += dup
            print(f"  New: {new}, Duplicates skipped: {dup}")

        if not dry_run:
            await db.commit()

        print(f"\n=== Total new: {total_new}, Duplicates skipped: {total_skipped_dup} ===")
        if dry_run:
            print("[DRY RUN] Use --no-dry-run to import.")


if __name__ == "__main__":
    dry_run = "--no-dry-run" not in sys.argv
    source_filter = None
    for arg in sys.argv[1:]:
        if arg.startswith("--source="):
            source_filter = arg.split("=", 1)[1]
    asyncio.run(run_import(dry_run=dry_run, source_filter=source_filter))
