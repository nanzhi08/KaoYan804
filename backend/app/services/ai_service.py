import uuid
import re
from typing import AsyncIterator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..ai_providers.deepseek_provider import DeepSeekProvider
from ..config import settings
from ..models.ai_conversation import AIConversation
from ..models.ai_training_example import AITrainingExample
from ..models.knowledge_point import KnowledgePoint
from ..models.question import Question

SYSTEM_PROMPT = """你是一位专业的考研804《数据结构与高级程序设计》辅导老师。

考试范围：C语言高级程序设计(70分) + 数据结构(80分)
参考书目：
  - 《数据结构》（C语言版 第2版）严蔚敏、李冬梅、吴伟民编，人民邮电出版社
  - 《C语言程序设计》（第4版）何钦铭、颜晖编，高等教育出版社
学校：上海第二工业大学

要求：
1. 用中文回答，讲解要结合考试重点
2. 讲解代码时使用C语言
3. 适当举例帮助理解
4. 当学生有疑问时，耐心解答并引导思考，而非直接给答案
5. 如果学生做错了题，先分析错误原因再给出正确解法"""

DOMAIN_TERMS = [
    "链表", "栈", "队列", "树", "二叉树", "图", "排序", "查找", "哈希",
    "指针", "数组", "结构体", "函数", "递归", "算法", "时间复杂度",
    "空间复杂度", "动态规划", "贪心", "回溯", "分治", "遍历",
    "DFS", "BFS", "C语言", "数据结构", "线性表", "堆", "最短路径",
    "折半查找", "平衡二叉树", "快速排序", "堆排序", "归并排序",
]


def _ensure_message_ids(messages: list[dict]) -> list[dict]:
    for msg in messages:
        if "id" not in msg:
            msg["id"] = str(uuid.uuid4())
    return messages


def _extract_keywords_from_text(text: str, max_keywords: int = 5) -> list[str]:
    found = []
    text_lower = text.lower()
    for term in DOMAIN_TERMS:
        if term.lower() in text_lower:
            found.append(term)
            if len(found) >= max_keywords:
                return found
    clean = re.sub(r'\s+', '', text)
    for i in range(len(clean) - 1):
        bigram = clean[i:i + 2]
        if any('\u4e00' <= c <= '\u9fff' for c in bigram):
            found.append(bigram)
        if len(found) >= max_keywords:
            break
    return found[:max_keywords]


def get_provider(provider_name: str):
    if provider_name == "deepseek":
        if not settings.DEEPSEEK_API_KEY:
            raise RuntimeError("AI服务未配置 DEEPSEEK_API_KEY，请先在环境变量或 .env 中设置后再使用。")
        return DeepSeekProvider()

    if provider_name == "claude":
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("AI服务未配置 ANTHROPIC_API_KEY，请先在环境变量或 .env 中设置后再使用。")
        return ClaudeProvider()

    if not settings.DEEPSEEK_API_KEY:
        raise RuntimeError("AI服务未配置 DEEPSEEK_API_KEY，请先在环境变量或 .env 中设置后再使用。")
    return DeepSeekProvider()


async def build_explain_prompt(db: AsyncSession, kp_id: int) -> str:
    result = await db.execute(select(KnowledgePoint).where(KnowledgePoint.id == kp_id))
    kp = result.scalar_one_or_none()
    if not kp:
        return "请讲解这个知识点。"
    return f"""请详细讲解以下知识点：

【知识点】{kp.name}
【所属章节】{kp.chapter}
【考试频率】{kp.exam_weight}
【难度】{'★' * kp.difficulty}

请包含以下内容：
1. 核心概念讲解
2. 考试重点和常见考点
3. 典型例题讲解（用C语言代码示例）
4. 易错点提醒

{'' if not kp.description else f'补充说明：{kp.description}'}"""


async def build_review_prompt(db: AsyncSession, question_id: int, user_answer: str) -> str:
    result = await db.execute(select(Question).where(Question.id == question_id))
    q = result.scalar_one_or_none()
    if not q:
        return f"请批改这个答案：{user_answer}"
    return f"""请批改以下题目的答案：

【题目】{q.content}
【题型】{q.type}
【参考答案】{q.answer}
【学生答案】{user_answer}

请分析：
1. 学生的答案是否正确
2. 如果错误，分析可能的原因
3. 给出正确的解题思路
4. 相关的知识点回顾"""


def _make_title(messages: list[dict], kp_id: int | None = None) -> str:
    """Generate conversation title from first user message."""
    for m in messages:
        if m["role"] == "user":
            content = m["content"].strip()
            # Remove common prefixes
            content = content.replace("请帮我讲解这道题目：", "").strip()
            content = content.replace("请帮我详细讲解【", "").replace("】这个知识点。", "").strip()
            # Truncate and clean
            title = content.split('\n')[0][:40]
            return title if title else "新对话"
    return "新对话"


async def get_or_create_conversation(
    db: AsyncSession,
    conversation_id: int | None,
    provider: str,
    kp_id: int | None = None,
    question_id: int | None = None,
    first_user_message: str = "",
    user_id: int | None = None,
) -> AIConversation:
    if conversation_id:
        result = await db.execute(
            select(AIConversation).where(
                AIConversation.id == conversation_id,
                AIConversation.user_id == user_id,
            )
        )
        conv = result.scalar_one_or_none()
        if conv:
            return conv

    title = first_user_message.split('\n')[0][:40] if first_user_message else "新对话"
    conv = AIConversation(
        user_id=user_id,
        provider=provider,
        knowledge_point_id=kp_id,
        question_id=question_id,
        title=title,
        messages=[],
    )
    db.add(conv)
    await db.commit()
    return conv


async def save_conversation(db: AsyncSession, conv: AIConversation, messages: list[dict]):
    conv.messages = messages
    await db.commit()


async def get_relevant_examples(
    db: AsyncSession,
    kp_id: int | None = None,
    user_message: str = "",
    limit: int = 3,
    user_id: int | None = None,
) -> list[AITrainingExample]:
    examples: list[AITrainingExample] = []

    # Strategy 1: same chapter
    if kp_id:
        kp_result = await db.execute(
            select(KnowledgePoint).where(KnowledgePoint.id == kp_id)
        )
        kp = kp_result.scalar_one_or_none()
        if kp and kp.chapter:
            result = await db.execute(
                select(AITrainingExample)
                .where(
                    AITrainingExample.chapter == kp.chapter,
                    AITrainingExample.is_active == True,
                    AITrainingExample.user_id == user_id,
                )
                .order_by(AITrainingExample.usage_count.asc())
                .limit(limit)
            )
            examples = list(result.scalars().all())

    # Strategy 2: keyword overlap
    existing_ids = {e.id for e in examples}
    if len(examples) < limit and user_message:
        keywords = _extract_keywords_from_text(user_message)
        for kw in keywords[:5]:
            remaining = limit - len(examples)
            if remaining <= 0:
                break
            result = await db.execute(
                select(AITrainingExample)
                .where(
                    AITrainingExample.keywords.like(f"%{kw}%"),
                    AITrainingExample.is_active == True,
                    AITrainingExample.user_id == user_id,
                    AITrainingExample.id.notin_(existing_ids) if existing_ids else True,
                )
                .order_by(AITrainingExample.usage_count.asc())
                .limit(remaining)
            )
            for e in result.scalars().all():
                if e.id not in existing_ids:
                    examples.append(e)
                    existing_ids.add(e.id)

    # Strategy 3: any active
    if len(examples) < limit:
        remaining = limit - len(examples)
        result = await db.execute(
            select(AITrainingExample)
            .where(
                AITrainingExample.is_active == True,
                AITrainingExample.user_id == user_id,
                AITrainingExample.id.notin_(existing_ids) if existing_ids else True,
            )
            .order_by(AITrainingExample.usage_count.asc())
            .limit(remaining)
        )
        examples.extend(result.scalars().all())

    for e in examples:
        e.usage_count = (e.usage_count or 0) + 1
    if examples:
        await db.commit()

    return examples


async def chat_stream(
    db: AsyncSession,
    provider_name: str,
    messages: list[dict],
    conversation_id: int | None = None,
    kp_id: int | None = None,
    question_id: int | None = None,
    user_id: int | None = None,
) -> AsyncIterator[tuple[str, AIConversation]]:
    _ensure_message_ids(messages)
    provider = get_provider(provider_name)
    first_msg = ""
    for m in messages:
        if m["role"] == "user":
            first_msg = m["content"]
            break
    conv = await get_or_create_conversation(db, conversation_id, provider_name, kp_id, question_id, first_msg, user_id=user_id)

    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if settings.ENABLE_FEW_SHOT:
        user_msg = ""
        for m in reversed(messages):
            if m["role"] == "user":
                user_msg = m["content"]
                break
        examples = await get_relevant_examples(
            db, kp_id=kp_id, user_message=user_msg,
            limit=settings.MAX_FEW_SHOT_EXAMPLES,
            user_id=user_id,
        )
        if examples:
            full_messages.append({
                "role": "system",
                "content": "以下是你之前回答过、获得学生好评的问答示例，请参考这些示例的详细程度、代码规范性和解释风格来回答当前问题：",
            })
            for i, e in enumerate(examples, 1):
                full_messages.append({
                    "role": "user",
                    "content": f"【参考示例{i}—学生问题】\n{e.user_question}",
                })
                full_messages.append({
                    "role": "assistant",
                    "content": f"【参考示例{i}—你的回答】\n{e.assistant_answer}",
                })
            full_messages.append({
                "role": "system",
                "content": "--- 以上是参考示例，以下是当前对话 ---\n请基于当前对话回答学生的最新问题，不要主动提及上述示例。",
            })

    full_messages.extend(messages)
    full_text = ""

    async for chunk in provider.chat_stream(full_messages):
        full_text += chunk
        yield chunk, conv

    messages.append({"role": "assistant", "content": full_text, "id": str(uuid.uuid4())})
    conv.messages = messages
    await db.commit()
