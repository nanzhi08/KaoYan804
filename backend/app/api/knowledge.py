from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.common import APIResponse
from ..schemas.knowledge import KnowledgePointDetail
from ..services import knowledge_service

router = APIRouter(prefix="/api/knowledge-points", tags=["知识管理"])


@router.get("")
async def list_knowledge_points(db: AsyncSession = Depends(get_db)):
    tree = await knowledge_service.get_knowledge_tree(db)
    return APIResponse(data=tree)


@router.get("/{kp_id}")
async def get_knowledge_point(kp_id: int, db: AsyncSession = Depends(get_db)):
    kp = await knowledge_service.get_knowledge_point(db, kp_id)
    if not kp:
        return APIResponse(code=404, message="知识点不存在")
    return APIResponse(data={
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
    })
