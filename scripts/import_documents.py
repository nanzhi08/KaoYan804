"""批量导入804资料包文件到资料管理系统"""
import sys
sys.path.insert(0, ".")

import asyncio
import os
import shutil
from pathlib import Path

from sqlalchemy import select
from app.database import async_session, init_db
from app.models.document import Document

from scripts.import_report import ImportReport, write_report

PACKAGE_DIR = Path(r"C:\Users\zhangsihai\Desktop\考研知识库系统\二工大804资料包")
UPLOAD_DIR = Path(r"C:\Users\zhangsihai\Desktop\考研知识库系统\data\uploads")

# File tagging rules: (relative_path_pattern, tags, is_question_source)
FILE_RULES = [
    # === Textbooks (document only, no question extraction) ===
    ("专业课考试书籍/C语言程序设计第四版", ["教材", "C_programming"], False),
    ("专业课考试书籍/数据结构 C语言版 第2版", ["教材", "data_structure"], False),
    ("专业课考试书籍/数据结构（C语言版）（第2版）-习题答案", ["教材", "data_structure", "习题答案"], False),

    # === Exam outlines ===
    ("2025考试大纲804", ["考纲", "2025", "C_programming", "data_structure"], False),
    ("2026考试大纲804", ["考纲", "2026", "C_programming", "data_structure"], False),

    # === Exam papers (document + question extraction later) ===
    ("2022-2025真题/2022年", ["真题", "2022", "C_programming", "data_structure"], True),
    ("2022-2025真题/2023年", ["真题", "2023", "C_programming", "data_structure"], True),
    ("2022-2025真题/2024年", ["真题", "2024", "C_programming", "data_structure"], True),
    ("2022-2025真题/25二工大", ["真题", "2025", "回忆版", "C_programming", "data_structure"], True),

    # === C knowledge notes ===
    ("C语言知识点总结/C语言学习笔记", ["笔记", "C_programming"], False),
    ("C语言知识点总结/C语言常考知识点", ["笔记", "C_programming"], False),
    ("C语言知识点总结/C语言知识点总结", ["笔记", "C_programming"], False),
    ("C语言知识点总结/C语言程序设计知识点总结", ["笔记", "C_programming"], False),
    ("C语言知识点总结/C语言课件", ["课件", "C_programming"], False),

    # === C question banks ===
    ("C语言知识点总结/题库1-", ["题库", "C_programming", "分章习题"], True),
    ("C语言知识点总结/题库2-", ["题库", "C_programming", "分章习题"], True),
    ("C语言知识点总结/题库3-", ["题库", "C_programming", "模拟卷"], True),
    ("C语言知识点总结/题库4-", ["题库", "C_programming", "程序改错"], True),
    ("C语言知识点总结/题库5-", ["题库", "C_programming", "期末试题"], True),
    ("C语言知识点总结/题库6-", ["题库", "C_programming", "程序填空"], True),
    ("C语言知识点总结/题库7-", ["题库", "C_programming", "模拟题"], True),
    ("C语言知识点总结/题库8-", ["题库", "C_programming", "模拟题"], True),
    ("C语言知识点总结/题库9-", ["题库", "C_programming", "经典题目"], True),
    ("C语言知识点总结/题库10-", ["题库", "C_programming", "复习题"], True),
    ("C语言知识点总结/题库11-", ["题库", "C_programming", "简答题"], True),

    # === C chapter exercises ===
    ("c语言各章节练习题/第1章", ["章节练习", "C_programming", "ch1.1"], True),
    ("c语言各章节练习题/第2章", ["章节练习", "C_programming", "ch1.1"], True),
    ("c语言各章节练习题/第3章", ["章节练习", "C_programming", "ch1.3"], True),
    ("c语言各章节练习题/第4章", ["章节练习", "C_programming", "ch1.4"], True),
    ("c语言各章节练习题/第5章", ["章节练习", "C_programming", "ch1.5"], True),
    ("c语言各章节练习题/第6章", ["章节练习", "C_programming", "ch1.6"], True),
    ("c语言各章节练习题/第7章", ["章节练习", "C_programming", "ch1.4"], True),
    ("c语言各章节练习题/第8章", ["章节练习", "C_programming", "ch1.2"], True),
    ("c语言各章节练习题/第9章", ["章节练习", "C_programming", "ch1.7"], True),

    # === DS notes ===
    ("数据结构/数据结构Markdown版", ["笔记", "data_structure"], True),
    ("数据结构/数据结构word版", ["笔记", "data_structure"], False),

    # === DS papers ===
    ("数据结构10套卷", ["试卷", "data_structure", "模拟卷"], True),
    ("数据结构校内期末试题/数据结构期末卷 (2)", ["试卷", "data_structure", "期末"], True),
    ("数据结构校内期末试题/数据结构期末卷.pdf", ["试卷", "data_structure", "期末"], True),

    # === Reference ===
    ("2025复试成绩", ["参考", "复试"], False),
]

# Files to skip (internal duplicates within package)
SKIP_PATTERNS = [
    "(1).pdf",  # Skip files with (1) suffix (duplicates)
    "资料分析总结报告.md",  # This is an analysis report, not study material
]


def get_tags(rel_path: str) -> tuple[list[str], bool]:
    """Determine tags for a file based on its relative path."""
    for pattern, tags, is_q in FILE_RULES:
        if pattern in rel_path.replace("\\", "/"):
            return tags, is_q
    return ["未分类"], False


def should_skip(rel_path: str) -> bool:
    for pat in SKIP_PATTERNS:
        if pat in rel_path:
            return True
    return False


async def import_documents():
    await init_db()
    report = ImportReport(script="import_documents.py", dry_run=False)

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    async with async_session() as db:
        result = await db.execute(select(Document))
        existing = {(d.original_name, d.file_size) for d in result.scalars().all()}

        imported = 0
        skipped_dup = 0
        skipped_pattern = 0
        skipped_type = 0
        errors = []

        for filepath in sorted(PACKAGE_DIR.rglob("*")):
            if not filepath.is_file():
                continue

            rel_path = str(filepath.relative_to(PACKAGE_DIR))

            if should_skip(rel_path):
                skipped_pattern += 1
                continue

            file_size = filepath.stat().st_size
            original_name = filepath.name
            file_ext = filepath.suffix.lower().lstrip(".")

            if file_ext not in ("pdf", "docx", "doc", "txt", "md", "png", "jpg", "jpeg", "ppt", "pptx"):
                skipped_type += 1
                continue

            # Check duplicate
            if (original_name, file_size) in existing:
                skipped_dup += 1
                continue

            tags, is_question_source = get_tags(rel_path)

            # Create unique filename
            base_name = original_name
            dest_name = base_name
            counter = 1
            while os.path.exists(UPLOAD_DIR / dest_name):
                name_part, ext = os.path.splitext(base_name)
                dest_name = f"{name_part}_{counter}{ext}"
                counter += 1

            # Copy file
            try:
                shutil.copy2(filepath, UPLOAD_DIR / dest_name)
            except Exception as e:
                error = f"Copy error {rel_path}: {e}"
                errors.append(error)
                continue

            # Create DB record
            doc = Document(
                filename=dest_name,
                original_name=original_name,
                file_type=file_ext,
                file_size=file_size,
                content_text="",  # Will be populated by OCR on demand
                tags=tags,
            )
            db.add(doc)
            existing.add((original_name, file_size))
            imported += 1

        await db.commit()

    report.counters = {
        "imported": imported,
        "skipped_db_duplicate": skipped_dup,
        "skipped_pattern": skipped_pattern,
        "skipped_unsupported_type": skipped_type,
        "errors": len(errors),
    }
    for error in errors:
        report.add_error(error)
    report_path = write_report(report)

    print(f"Import complete:")
    print(f"  Imported: {imported}")
    print(f"  Skipped (DB duplicate): {skipped_dup}")
    print(f"  Skipped (pattern): {skipped_pattern}")
    print(f"  Skipped (unsupported type): {skipped_type}")
    print(f"  Report: {report_path}")
    if errors:
        print(f"  Errors: {len(errors)}")
        for e in errors[:10]:
            print(f"    {e}")


if __name__ == "__main__":
    asyncio.run(import_documents())
