from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..schemas.common import APIResponse
from ..models.practice_record import PracticeRecord
from ..models.question import Question
from ..models.knowledge_point import KnowledgePoint
from ..models.knowledge_mastery import KnowledgeMastery
from ..time_utils import local_today_start_as_utc_naive

router = APIRouter(prefix="/api/progress", tags=["进度统计"])


@router.get("/overview")
async def progress_overview(db: AsyncSession = Depends(get_db)):
    total_result = await db.execute(select(func.count(PracticeRecord.id)))
    total_attempts = total_result.scalar()

    correct_result = await db.execute(
        select(func.count(PracticeRecord.id)).where(PracticeRecord.is_correct == True)
    )
    total_correct = correct_result.scalar()
    accuracy = round(total_correct / total_attempts * 100, 1) if total_attempts > 0 else 0

    # Count per part - correctly join PracticeRecord -> Question
    c_result = await db.execute(
        select(func.count(PracticeRecord.id))
        .join(Question, PracticeRecord.question_id == Question.id)
        .where(Question.part == "C_programming")
    )
    c_attempts = c_result.scalar()

    ds_result = await db.execute(
        select(func.count(PracticeRecord.id))
        .join(Question, PracticeRecord.question_id == Question.id)
        .where(Question.part == "data_structure")
    )
    ds_attempts = ds_result.scalar()

    # Accuracy per part
    c_correct = await db.execute(
        select(func.count(PracticeRecord.id))
        .join(Question, PracticeRecord.question_id == Question.id)
        .where(Question.part == "C_programming", PracticeRecord.is_correct == True)
    )
    c_correct_val = c_correct.scalar()

    ds_correct = await db.execute(
        select(func.count(PracticeRecord.id))
        .join(Question, PracticeRecord.question_id == Question.id)
        .where(Question.part == "data_structure", PracticeRecord.is_correct == True)
    )
    ds_correct_val = ds_correct.scalar()

    today = local_today_start_as_utc_naive()
    today_result = await db.execute(
        select(func.count(PracticeRecord.id)).where(PracticeRecord.created_at >= today)
    )
    today_attempts = today_result.scalar() or 0

    now = datetime.now()
    due_result = await db.execute(
        select(func.count(KnowledgeMastery.id)).where(
            or_(
                KnowledgeMastery.next_review_at.is_(None),
                KnowledgeMastery.next_review_at <= now,
            )
        )
    )
    due_review_count = due_result.scalar() or 0

    weak_result = await db.execute(
        select(func.count(KnowledgeMastery.id)).where(KnowledgeMastery.mastery_level < 0.4)
    )
    weak_knowledge_count = weak_result.scalar() or 0

    daily_target = min(
        30,
        max(
            10,
            10 + min(10, due_review_count * 2) + min(10, (weak_knowledge_count + 9) // 10),
        ),
    )

    # Recently practiced
    recent_result = await db.execute(
        select(PracticeRecord).order_by(PracticeRecord.created_at.desc()).limit(10)
    )
    recent = recent_result.scalars().all()

    return APIResponse(data={
        "total_attempts": total_attempts,
        "total_correct": total_correct,
        "accuracy": accuracy,
        "c_attempts": c_attempts,
        "ds_attempts": ds_attempts,
        "c_accuracy": round(c_correct_val / c_attempts * 100, 1) if c_attempts > 0 else 0,
        "ds_accuracy": round(ds_correct_val / ds_attempts * 100, 1) if ds_attempts > 0 else 0,
        "recent_attempts": len(recent),
        "today_attempts": today_attempts,
        "daily_target": daily_target,
        "due_review_count": due_review_count,
        "weak_knowledge_count": weak_knowledge_count,
    })


@router.get("/detail")
async def progress_detail(db: AsyncSession = Depends(get_db)):
    # Chapter-level progress - use join to avoid N+1
    result = await db.execute(
        select(KnowledgePoint).options(selectinload(KnowledgePoint.mastery))
        .where(KnowledgePoint.parent_id.isnot(None), KnowledgePoint.chapter != "")
        .order_by(KnowledgePoint.part, KnowledgePoint.chapter)
    )
    kps = result.unique().scalars().all()

    chapters = []
    for kp in kps:
        mastery = kp.mastery
        chapters.append({
            "id": kp.id,
            "name": kp.name,
            "part": kp.part,
            "chapter": kp.chapter,
            "difficulty": kp.difficulty,
            "exam_weight": kp.exam_weight,
            "mastery_level": round(mastery.mastery_level * 100, 1) if mastery else 0,
            "total_attempts": mastery.total_attempts if mastery else 0,
            "next_review_at": mastery.next_review_at.isoformat() if mastery and mastery.next_review_at else None,
        })

    return APIResponse(data=chapters)


@router.get("/radar")
async def progress_radar(db: AsyncSession = Depends(get_db)):
    part_labels = {"C_programming": "C语言程序设计", "data_structure": "数据结构"}

    result = await db.execute(
        select(KnowledgePoint).options(selectinload(KnowledgePoint.mastery))
        .where(KnowledgePoint.parent_id.isnot(None), KnowledgePoint.chapter != "")
        .order_by(KnowledgePoint.part, KnowledgePoint.chapter)
    )
    kps = result.unique().scalars().all()

    data = []
    for kp in kps:
        mastery = kp.mastery
        data.append({
            "chapter": kp.chapter,
            "name": kp.name,
            "part": part_labels.get(kp.part, kp.part),
            "mastery": round(mastery.mastery_level * 100, 1) if mastery else 0,
        })

    return APIResponse(data=data)
