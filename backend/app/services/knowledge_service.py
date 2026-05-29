from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.knowledge_point import KnowledgePoint


async def get_knowledge_tree(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(KnowledgePoint)
        .where(KnowledgePoint.parent_id.is_(None))
        .options(selectinload(KnowledgePoint.children))
        .order_by(KnowledgePoint.order)
    )
    roots = result.scalars().all()

    async def build_node(kp: KnowledgePoint) -> dict:
        children_result = await db.execute(
            select(KnowledgePoint)
            .where(KnowledgePoint.parent_id == kp.id)
            .options(selectinload(KnowledgePoint.children))
            .order_by(KnowledgePoint.order)
        )
        children = children_result.scalars().all()

        return {
            "id": kp.id,
            "parent_id": kp.parent_id,
            "name": kp.name,
            "description": kp.description or "",
            "part": kp.part,
            "chapter": kp.chapter or "",
            "order": kp.order,
            "difficulty": kp.difficulty,
            "exam_weight": kp.exam_weight or "",
            "ai_explanation": kp.ai_explanation or "",
            "children": [await build_node(c) for c in children],
        }

    return [await build_node(r) for r in roots]


async def get_knowledge_point(db: AsyncSession, kp_id: int) -> KnowledgePoint | None:
    result = await db.execute(
        select(KnowledgePoint).where(KnowledgePoint.id == kp_id)
    )
    return result.scalar_one_or_none()
