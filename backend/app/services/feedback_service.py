import hashlib
import re
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.ai_feedback import AIFeedback
from ..models.ai_training_example import AITrainingExample
from ..models.ai_conversation import AIConversation
from ..models.knowledge_point import KnowledgePoint

DOMAIN_TERMS = [
    "链表", "栈", "队列", "树", "二叉树", "图", "排序", "查找", "哈希",
    "指针", "数组", "结构体", "函数", "递归", "算法", "时间复杂度",
    "空间复杂度", "动态规划", "贪心", "回溯", "分治", "遍历",
    "DFS", "BFS", "C语言", "数据结构", "线性表", "串", "广义表",
    "文件", "堆", "栈和队列", "二叉树遍历", "哈夫曼", "最短路径",
    "最小生成树", "拓扑排序", "关键路径", "折半查找", "平衡二叉树",
    "B树", "散列表", "直接插入", "希尔排序", "冒泡", "快速排序",
    "堆排序", "归并排序", "基数排序", "选择排序",
]


def _extract_keywords(text: str, max_keywords: int = 10) -> str:
    found = []
    text_lower = text.lower()
    for term in DOMAIN_TERMS:
        if term.lower() in text_lower:
            found.append(term)
            if len(found) >= max_keywords:
                return ",".join(found)

    clean = re.sub(r'\s+', '', text)
    bigrams = []
    for i in range(len(clean) - 1):
        bigram = clean[i:i + 2]
        if any('\u4e00' <= c <= '\u9fff' for c in bigram):
            bigrams.append(bigram)
    found.extend(bigrams[:max_keywords - len(found)])

    return ",".join(found[:max_keywords])


async def save_feedback_and_extract_example(
    db: AsyncSession,
    data,
) -> tuple[AIFeedback, AITrainingExample | None]:
    feedback = AIFeedback(
        conversation_id=data.conversation_id,
        message_id=data.message_id,
        message_index=data.message_index,
        rating=data.rating,
        comment=data.comment,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    if data.rating != 1:
        return feedback, None

    example = await _extract_example(db, data, feedback)
    return feedback, example


async def _extract_example(db, data, feedback) -> AITrainingExample | None:
    result = await db.execute(
        select(AIConversation).where(AIConversation.id == data.conversation_id)
    )
    conv = result.scalar_one_or_none()
    if not conv or not conv.messages:
        return None

    messages = conv.messages
    idx = data.message_index

    if idx <= 0 or idx >= len(messages):
        return None
    if messages[idx].get("role") != "assistant":
        return None
    if messages[idx - 1].get("role") != "user":
        return None

    user_question = messages[idx - 1]["content"]
    assistant_answer = messages[idx]["content"]

    if len(user_question.strip()) < 5 or len(assistant_answer.strip()) < 20:
        return None

    qhash = hashlib.sha256(user_question.strip().encode()).hexdigest()[:16]

    existing = await db.execute(
        select(AITrainingExample).where(
            AITrainingExample.keywords.like(f"%{qhash}%")
        )
    )
    if existing.scalar_one_or_none():
        return None

    chapter = ""
    part = ""
    if conv.knowledge_point_id:
        kp_result = await db.execute(
            select(KnowledgePoint).where(KnowledgePoint.id == conv.knowledge_point_id)
        )
        kp = kp_result.scalar_one_or_none()
        if kp:
            chapter = kp.chapter or ""
            part = kp.part or ""

    keywords = _extract_keywords(user_question) + "," + qhash

    example = AITrainingExample(
        conversation_id=conv.id,
        feedback_id=feedback.id,
        user_question=user_question.strip(),
        assistant_answer=assistant_answer.strip(),
        knowledge_point_id=conv.knowledge_point_id,
        chapter=chapter,
        part=part,
        keywords=keywords,
    )
    db.add(example)
    await db.commit()
    await db.refresh(example)
    return example
