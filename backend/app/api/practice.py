from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..schemas.common import APIResponse
from ..schemas.question import PracticeSubmit
from ..services import question_service
from ..models.practice_record import PracticeRecord
from ..time_utils import local_today_start_as_utc_naive

router = APIRouter(prefix="/api/practice", tags=["练习"])


@router.post("/submit")
async def submit_practice(
    data: PracticeSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await question_service.submit_practice(db, data.model_dump(), current_user.id)
    if result is None:
        return APIResponse(code=404, message="题目不存在")
    return APIResponse(data=result)


@router.get("/history")
async def practice_history(
    page: int = 1,
    page_size: int = 20,
    mode: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records, total = await question_service.get_practice_history(
        db, page, page_size, mode, current_user.id
    )
    return APIResponse(data={
        "items": [
            {
                "id": r.id,
                "question_id": r.question_id,
                "user_answer": r.user_answer,
                "is_correct": r.is_correct,
                "time_spent": r.time_spent,
                "practice_mode": r.practice_mode,
                "created_at": r.created_at.isoformat(),
                "question_content": r.question.content[:100] if r.question else "",
                "question_type": r.question.type if r.question else "",
                "correct_answer": r.question.answer if r.question else "",
            }
            for r in records
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/wrong-questions")
async def get_wrong_questions(
    count: int = Query(default=20, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ids = await question_service.get_wrong_question_ids(db, limit=count, user_id=current_user.id)
    if not ids:
        return APIResponse(data=[])

    questions = await question_service.get_questions_by_ids(db, ids)
    id_order = {qid: i for i, qid in enumerate(ids)}
    questions.sort(key=lambda q: id_order.get(q.id, 999))

    return APIResponse(data=[question_service.question_to_dict(q) for q in questions])


@router.get("/stats")
async def practice_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base_q = select(func.count(PracticeRecord.id)).where(PracticeRecord.user_id == current_user.id)
    total_val = (await db.execute(base_q)).scalar() or 0
    correct_val = (await db.execute(
        select(func.count(PracticeRecord.id)).where(PracticeRecord.user_id == current_user.id, PracticeRecord.is_correct == True)
    )).scalar() or 0
    wrong_val = (await db.execute(
        select(func.count(PracticeRecord.id)).where(PracticeRecord.user_id == current_user.id, PracticeRecord.is_correct == False)
    )).scalar() or 0
    today = local_today_start_as_utc_naive()
    today_val = (await db.execute(
        select(func.count(PracticeRecord.id)).where(PracticeRecord.user_id == current_user.id, PracticeRecord.created_at >= today)
    )).scalar() or 0

    return APIResponse(data={
        "total": total_val,
        "correct": correct_val,
        "wrong": wrong_val,
        "today": today_val,
        "accuracy": round(correct_val / total_val * 100, 1) if total_val > 0 else 0,
    })
