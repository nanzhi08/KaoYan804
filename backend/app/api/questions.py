from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import get_current_user
from ..schemas.common import APIResponse, PaginatedData
from ..schemas.question import QuestionCreate, PracticeSubmit
from ..services import question_service

router = APIRouter(prefix="/api/questions", tags=["题库管理"])


@router.get("")
async def list_questions(current_user = Depends(get_current_user), 
    type: str | None = Query(None),
    part: str | None = Query(None),
    difficulty: int | None = Query(None),
    knowledge_point_id: int | None = Query(None),
    chapter: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    questions, total = await question_service.get_questions(
        db, type, part, difficulty, knowledge_point_id, chapter, page, page_size
    )
    return APIResponse(data=PaginatedData(
        items=[question_service.question_to_dict(q) for q in questions],
        total=total,
        page=page,
        page_size=page_size,
    ))


@router.get("/random")
async def random_questions(current_user = Depends(get_current_user), 
    count: int = Query(10, ge=1, le=50),
    type: str | None = Query(None),
    part: str | None = Query(None),
    difficulty: int | None = Query(None),
    knowledge_point_ids: str | None = Query(None),
    chapter: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    kp_ids = [int(x) for x in knowledge_point_ids.split(",")] if knowledge_point_ids else None
    questions = await question_service.get_random_questions(
        db, count, type, part, difficulty, kp_ids, chapter
    )
    return APIResponse(data=[question_service.question_to_dict(q) for q in questions])


@router.get("/chapters")
async def list_chapters(current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    chapters = await question_service.get_chapter_summary(db)
    return APIResponse(data=chapters)


@router.get("/{q_id}")
async def get_question(q_id: int, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    q = await question_service.get_question(db, q_id)
    if not q:
        return APIResponse(code=404, message="题目不存在")
    return APIResponse(data=question_service.question_to_dict(q))


@router.post("")
async def create_question(data: QuestionCreate, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    q = await question_service.create_question(db, data.model_dump())
    return APIResponse(data=question_service.question_to_dict(q))


@router.delete("/{q_id}")
async def delete_question(q_id: int, current_user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from sqlalchemy import delete as sa_delete
    from ..models.question import Question, QuestionKnowledgePoint

    q = await question_service.get_question(db, q_id)
    if not q:
        return APIResponse(code=404, message="题目不存在")

    await db.execute(
        sa_delete(QuestionKnowledgePoint).where(QuestionKnowledgePoint.question_id == q_id)
    )
    await db.execute(sa_delete(Question).where(Question.id == q_id))
    await db.commit()
    return APIResponse(message="删除成功")
