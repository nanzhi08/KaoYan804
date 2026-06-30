import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from datetime import datetime, timedelta

from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..schemas.common import APIResponse
from ..models.knowledge_point import KnowledgePoint
from ..models.knowledge_mastery import KnowledgeMastery
from ..models.question import Question, QuestionKnowledgePoint

router = APIRouter(prefix="/api/review", tags=["复习"])


def sm2_algorithm(mastery: KnowledgeMastery, quality: int):
    if quality < 0 or quality > 5:
        raise ValueError("quality must be 0-5")
    mastery.mastery_level = mastery.mastery_level or 0.0
    mastery.ease_factor = mastery.ease_factor or 2.5
    mastery.interval_days = mastery.interval_days or 0
    mastery.repetitions = mastery.repetitions or 0
    mastery.total_attempts = mastery.total_attempts or 0
    mastery.correct_attempts = mastery.correct_attempts or 0
    now = datetime.now()
    if quality >= 3:
        if mastery.repetitions == 0:
            mastery.interval_days = 1
        elif mastery.repetitions == 1:
            mastery.interval_days = 6
        else:
            mastery.interval_days = round(mastery.interval_days * mastery.ease_factor)
        mastery.repetitions += 1
    else:
        mastery.repetitions = 0
        mastery.interval_days = 1
    mastery.ease_factor = max(1.3, mastery.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
    mastery.mastery_level = min(1.0, (mastery.mastery_level * 0.7 + (quality / 5.0) * 0.3))
    mastery.last_reviewed_at = now
    mastery.next_review_at = now + timedelta(days=mastery.interval_days)
    mastery.total_attempts += 1
    if quality >= 3:
        mastery.correct_attempts += 1
    return mastery


@router.get("/due")
async def get_due_reviews(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        now = datetime.now()
        result = await db.execute(
            select(KnowledgeMastery)
            .where(
                KnowledgeMastery.user_id == current_user.id,
                or_(KnowledgeMastery.next_review_at.is_(None), KnowledgeMastery.next_review_at <= now),
            )
            .order_by(KnowledgeMastery.next_review_at.isnot(None), KnowledgeMastery.next_review_at)
            .limit(20)
        )
        due_items = result.scalars().all()
        due_data = []
        for mastery in due_items:
            kp_result = await db.execute(select(KnowledgePoint).where(KnowledgePoint.id == mastery.knowledge_point_id))
            kp = kp_result.scalar_one_or_none()
            if not kp:
                continue
            q_result = await db.execute(
                select(Question)
                .join(QuestionKnowledgePoint, Question.id == QuestionKnowledgePoint.question_id)
                .where(QuestionKnowledgePoint.knowledge_point_id == mastery.knowledge_point_id)
                .limit(1)
            )
            question = q_result.scalar_one_or_none()
            due_data.append({
                "mastery_id": mastery.id, "knowledge_point_id": kp.id,
                "name": kp.name, "chapter": kp.chapter, "part": kp.part,
                "mastery_level": round((mastery.mastery_level or 0.0) * 100, 1),
                "ease_factor": round(mastery.ease_factor or 2.5, 2),
                "interval_days": mastery.interval_days or 0,
                "repetitions": mastery.repetitions or 0,
                "next_review_at": mastery.next_review_at.isoformat() if mastery.next_review_at else None,
                "sample_question": {
                    "id": question.id,
                    "content": question.content[:100],
                    "type": question.type,
                } if question else None,
            })
        return APIResponse(data={"due_count": len(due_data), "items": due_data})
    except Exception:
        logging.getLogger(__name__).exception("get_due_reviews failed")
        raise HTTPException(status_code=500, detail="review data query failed")


@router.post("/{mastery_id}/review")
async def submit_review(
    mastery_id: int, quality: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if quality < 0 or quality > 5:
        raise HTTPException(status_code=400, detail="quality must be 0-5")
    result = await db.execute(
        select(KnowledgeMastery).where(
            KnowledgeMastery.id == mastery_id,
            KnowledgeMastery.user_id == current_user.id,
        )
    )
    mastery = result.scalar_one_or_none()
    if not mastery:
        raise HTTPException(status_code=404, detail="mastery record not found")
    mastery = sm2_algorithm(mastery, quality)
    await db.commit()
    return APIResponse(data={
        "mastery_id": mastery.id,
        "mastery_level": round((mastery.mastery_level or 0.0) * 100, 1),
        "ease_factor": round(mastery.ease_factor or 2.5, 2),
        "interval_days": mastery.interval_days or 0,
        "repetitions": mastery.repetitions or 0,
        "next_review_at": mastery.next_review_at.isoformat() if mastery.next_review_at else None,
    })


@router.get("/stats")
async def review_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        now = datetime.now()
        total_result = await db.execute(
            select(func.count(KnowledgeMastery.id)).where(KnowledgeMastery.user_id == current_user.id)
        )
        total = total_result.scalar()
        due_result = await db.execute(
            select(func.count(KnowledgeMastery.id)).where(
                KnowledgeMastery.user_id == current_user.id,
                or_(KnowledgeMastery.next_review_at.is_(None), KnowledgeMastery.next_review_at <= now),
            )
        )
        due_now = due_result.scalar()
        avg_result = await db.execute(
            select(func.avg(KnowledgeMastery.mastery_level)).where(KnowledgeMastery.user_id == current_user.id)
        )
        avg_mastery = round((avg_result.scalar() or 0) * 100, 1)
        week_later = now + timedelta(days=7)
        week_result = await db.execute(
            select(func.count(KnowledgeMastery.id)).where(
                KnowledgeMastery.user_id == current_user.id,
                or_(KnowledgeMastery.next_review_at.is_(None), KnowledgeMastery.next_review_at <= week_later),
            )
        )
        due_this_week = week_result.scalar()
        msg = f"{due_now} knowledge points due, {due_this_week} this week" if due_now > 0 else "No due reviews, keep it up!"
        return APIResponse(data={
            "total_knowledge_points": total, "average_mastery": avg_mastery,
            "due_now": due_now, "due_this_week": due_this_week, "message": msg,
        })
    except Exception:
        logging.getLogger(__name__).exception("review_stats failed")
        raise HTTPException(status_code=500, detail="review stats query failed")
