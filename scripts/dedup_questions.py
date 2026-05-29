"""通用题目去重脚本 - 基于 content 归一化 + SHA256 检测重复题目"""
import sys
sys.path.insert(0, ".")

import asyncio
import hashlib
import re
from collections import defaultdict

from sqlalchemy import select, delete as sa_delete
from app.database import async_session, init_db
from app.models.question import Question, QuestionKnowledgePoint


def normalize_content(text: str) -> str:
    """归一化题目内容：去空白、转小写、统一标点"""
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


async def find_duplicates(dry_run: bool = True):
    await init_db()

    async with async_session() as db:
        result = await db.execute(select(Question).order_by(Question.id))
        questions = result.scalars().all()

        groups = defaultdict(list)
        for q in questions:
            h = content_hash(q.content)
            groups[h].append(q)

        duplicates = {h: qs for h, qs in groups.items() if len(qs) > 1}

        if not duplicates:
            print(f"检查了 {len(questions)} 道题目，未发现重复。")
            return

        total_dup = sum(len(qs) - 1 for qs in duplicates.values())
        print(f"检查了 {len(questions)} 道题目，发现 {len(duplicates)} 组重复（共 {total_dup} 条多余记录）：\n")

        for h, qs in duplicates.items():
            keep = qs[0]
            to_delete = qs[1:]
            print(f"  保留 ID={keep.id} \"{keep.content[:60]}...\"")
            for qd in to_delete:
                print(f"    -> 删除 ID={qd.id} (重复)")
            print()

            if not dry_run:
                for qd in to_delete:
                    await db.execute(
                        sa_delete(QuestionKnowledgePoint).where(
                            QuestionKnowledgePoint.question_id == qd.id
                        )
                    )
                    await db.execute(sa_delete(Question).where(Question.id == qd.id))

        if dry_run:
            print(f"[DRY RUN] 将删除 {total_dup} 条重复题目。使用 --no-dry-run 执行实际删除。")
        else:
            await db.commit()
            print(f"已删除 {total_dup} 条重复题目。")


if __name__ == "__main__":
    dry_run = "--no-dry-run" not in sys.argv
    asyncio.run(find_duplicates(dry_run=dry_run))
