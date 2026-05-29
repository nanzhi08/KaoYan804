"""从数据结构Markdown版笔记中解析全部题目并导入题库"""
import asyncio
import hashlib
import re
import sys
sys.path.insert(0, ".")

from sqlalchemy import select
from app.database import async_session, init_db
from app.models.knowledge_point import KnowledgePoint
from app.models.question import Question, QuestionKnowledgePoint

MD_PATH = r"C:\Users\zhangsihai\Desktop\考研知识库系统\二工大804资料包\数据结构\数据结构Markdown版.md"

CHAPTER_MAP = {
    "一": "2.1", "二": "2.2", "三": "2.3", "四": "2.4",
    "五": "2.5", "六": "2.6", "七": "2.7", "八": "2.8",
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


def parse_ds_markdown(filepath: str) -> list[dict]:
    """Parse DS Markdown file into list of question dicts."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    chapters = []
    current_chapter = None
    current_section_start = 0

    for i, line in enumerate(lines):
        m = re.match(r"^#\s+([一二三四五六七八])[、．]\s*", line)
        if m:
            if current_chapter is not None:
                chapters.append((current_chapter, current_section_start, i))
            current_chapter = CHAPTER_MAP[m.group(1)]
            current_section_start = i
    if current_chapter is not None:
        chapters.append((current_chapter, current_section_start, len(lines)))

    questions = []

    for chapter, start, end in chapters:
        # Find exercise section within this chapter
        exercise_start = None
        for i in range(start, end):
            if re.match(r"^##\s*第.*章.*习题", lines[i]) or \
               re.match(r"^##\s*第.*章.*课后习题", lines[i]):
                exercise_start = i
                break
        if exercise_start is None:
            continue

        # Find next subsection after exercises to bound the exercise section
        exercise_end = end
        for i in range(exercise_start + 1, end):
            if re.match(r"^##\s+", lines[i]) and "习题" not in lines[i]:
                exercise_end = i
                break

        # Extract questions from exercise section
        q_lines = lines[exercise_start:exercise_end]
        text = "".join(q_lines)

        # Split by （N）at start of lines (after newline)
        blocks = re.split(r"\n(?=（\d+）)", text)
        # Also handle the first question if it starts with （N）
        if not blocks:
            continue

        for block in blocks:
            # Each block should be: （N）question_content \n> 答案：X \n> 解释：...
            qm = re.match(r"（(\d+)）\s*(.+)", block, re.DOTALL)
            if not qm:
                continue

            q_num = qm.group(1)
            q_body = qm.group(2)

            # Must have an answer marker
            ans_m = re.search(r">\s*答案[：:]\s*(.+)", q_body)
            if not ans_m:
                continue

            answer = ans_m.group(1).strip()
            q_text = q_body[:ans_m.start()]

            # Extract explanation
            exp_m = re.search(r">\s*解释[：:]\s*(.+)", q_body[ans_m.end():])
            explanation = exp_m.group(1).strip() if exp_m else ""

            # Clean question text: remove trailing whitespace, collapse blank lines
            q_text = re.sub(r"\n{3,}", "\n\n", q_text).strip()
            if not q_text or len(q_text) < 5:
                continue

            # Parse options: handle multiple formats
            # Format 1: A．xxx   B．xxx\nC．xxx   D．xxx  (2 pairs per line)
            # Format 2: A．xxx\nB．xxx\nC．xxx\nD．xxx  (each on own line)
            # Format 3: A. xxx B. xxx C. xxx D. xxx  (all on one line)
            options = {}

            # First try: find all [A-D] markers with their text
            opt_markers = list(re.finditer(r"([A-D])[．.\s]\s*", q_text))
            if len(opt_markers) >= 2:
                for i, m in enumerate(opt_markers):
                    letter = m.group(1)
                    start = m.end()
                    end = opt_markers[i + 1].start() if i + 1 < len(opt_markers) else len(q_text)
                    txt = q_text[start:end].strip()
                    txt = re.sub(r"\s*\n\s*", " ", txt)
                    txt = re.sub(r"\s+", " ", txt)
                    options[letter] = txt.strip()

                q_content = q_text[:opt_markers[0].start()].strip()
                q_content = re.sub(r"\n{3,}", "\n\n", q_content).strip()

            if not q_content or len(q_content) < 5:
                continue

            # Determine question type
            q_type = "single_choice"
            if not options:
                if re.search(r"```|#include|int\s+main|void\s+\w+\(", q_content):
                    if re.search(r"时间复杂|复杂度|频度", q_text):
                        q_type = "analysis"
                    else:
                        q_type = "program_reading"
                elif re.match(r"^O\(", answer):
                    q_type = "analysis"
                else:
                    q_type = "short_answer"

            difficulty = 3 if len(q_content) > 200 else 2

            questions.append({
                "type": q_type,
                "part": "data_structure",
                "difficulty": difficulty,
                "content": q_content[:2000],
                "options": options if options else None,
                "answer": answer[:500],
                "explanation": explanation[:2000] if explanation else "",
                "source": "数据结构Markdown版笔记",
                "kp_chapter": chapter,
            })

    return questions


async def run_import(dry_run: bool = True):
    await init_db()

    print(f"解析 MD 文件: {MD_PATH}")
    parsed = parse_ds_markdown(MD_PATH)
    print(f"解析到 {len(parsed)} 道题目\n")

    async with async_session() as db:
        # Get existing content hashes
        result = await db.execute(select(Question))
        existing = result.scalars().all()
        existing_hashes = {content_hash(q.content): q for q in existing}
        print(f"数据库中已有 {len(existing)} 道题目")

        # Get chapter-level knowledge points
        kp_result = await db.execute(
            select(KnowledgePoint).where(
                KnowledgePoint.chapter != "",
                KnowledgePoint.parent_id.isnot(None),
                KnowledgePoint.part == "data_structure",
            )
        )
        kps = kp_result.scalars().all()
        kp_by_chapter = {}
        for kp in kps:
            ch = kp.chapter
            if ch not in kp_by_chapter:
                kp_by_chapter[ch] = kp
        print(f"知识点章节映射: {list(kp_by_chapter.keys())}")

        new_count = 0
        skip_count = 0
        to_import = []

        for q_data in parsed:
            h = content_hash(q_data["content"])
            if h in existing_hashes:
                skip_count += 1
                continue

            chapter = q_data.pop("kp_chapter")
            kp = kp_by_chapter.get(chapter)
            if not kp:
                skip_count += 1
                continue

            q_data["knowledge_point_ids"] = [kp.id]
            to_import.append(q_data)
            new_count += 1

        print(f"新题目: {new_count}, 跳过(已存在/无章节): {skip_count}")

        if dry_run:
            print(f"\n[DRY RUN] 将导入 {len(to_import)} 道新题目。")
            if to_import:
                print("\n预览前 10 道:")
                for qd in to_import[:10]:
                    print(f"  [{qd['kp_chapter'] if 'kp_chapter' in qd else ''}] {qd['content'][:80]}...")
            return

        # Import new questions
        for q_data in to_import:
            kp_ids = q_data.pop("knowledge_point_ids", [])
            q = Question(**q_data)
            db.add(q)
            await db.flush()
            for kp_id in kp_ids:
                db.add(QuestionKnowledgePoint(question_id=q.id, knowledge_point_id=kp_id))

        await db.commit()
        print(f"\n成功导入 {len(to_import)} 道新题目！")


if __name__ == "__main__":
    dry_run = "--no-dry-run" not in sys.argv
    asyncio.run(run_import(dry_run=dry_run))
