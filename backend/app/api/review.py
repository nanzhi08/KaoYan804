from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from datetime import datetime, timedelta

from ..database import get_db
from ..schemas.common import APIResponse
from ..models.knowledge_point import KnowledgePoint
from ..models.knowledge_mastery import KnowledgeMastery
from ..models.question import Question, QuestionKnowledgePoint

router = APIRouter(prefix="/api/review", tags=["复习计划"])


def sm2_algorithm(mastery: KnowledgeMastery, quality: int):
    """SM-2 间隔重复算法
    quality: 0-5, where 0=complete blackout, 5=perfect response
    """
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
        # Correct response
        if mastery.repetitions == 0:
            mastery.interval_days = 1
        elif mastery.repetitions == 1:
            mastery.interval_days = 6
        else:
            mastery.interval_days = round(mastery.interval_days * mastery.ease_factor)

        mastery.repetitions += 1
    else:
        # Incorrect - reset
        mastery.repetitions = 0
        mastery.interval_days = 1

    # Update ease factor: EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
    mastery.ease_factor = max(1.3, mastery.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

    # Update mastery level: simple rolling average based on quality
    mastery.mastery_level = min(1.0, (mastery.mastery_level * 0.7 + (quality / 5.0) * 0.3))

    mastery.last_reviewed_at = now
    mastery.next_review_at = now + timedelta(days=mastery.interval_days)
    mastery.total_attempts += 1
    if quality >= 3:
        mastery.correct_attempts += 1

    return mastery


@router.get("/due")
async def get_due_reviews(db: AsyncSession = Depends(get_db)):
    """获取当前到期的复习知识点列表"""
    now = datetime.now()

    result = await db.execute(
        select(KnowledgeMastery)
        .where(or_(KnowledgeMastery.next_review_at.is_(None), KnowledgeMastery.next_review_at <= now))
        .order_by(KnowledgeMastery.next_review_at.isnot(None), KnowledgeMastery.next_review_at)
        .limit(20)
    )
    due_items = result.scalars().all()

    due_data = []
    for mastery in due_items:
        # Get the knowledge point name
        kp_result = await db.execute(
            select(KnowledgePoint).where(KnowledgePoint.id == mastery.knowledge_point_id)
        )
        kp = kp_result.scalar_one_or_none()
        if not kp:
            continue

        # Get a sample question for this knowledge point
        q_result = await db.execute(
            select(Question)
            .join(QuestionKnowledgePoint, Question.id == QuestionKnowledgePoint.question_id)
            .where(QuestionKnowledgePoint.knowledge_point_id == mastery.knowledge_point_id)
            .limit(1)
        )
        question = q_result.scalar_one_or_none()

        due_data.append({
            "mastery_id": mastery.id,
            "knowledge_point_id": kp.id,
            "name": kp.name,
            "chapter": kp.chapter,
            "part": kp.part,
            "mastery_level": round(mastery.mastery_level * 100, 1),
            "ease_factor": round(mastery.ease_factor, 2),
            "interval_days": mastery.interval_days,
            "repetitions": mastery.repetitions,
            "next_review_at": mastery.next_review_at.isoformat() if mastery.next_review_at else None,
            "sample_question": {
                "id": question.id,
                "content": question.content[:100],
                "type": question.type,
            } if question else None,
        })

    return APIResponse(data={
        "due_count": len(due_data),
        "items": due_data,
    })


@router.post("/{mastery_id}/review")
async def submit_review(mastery_id: int, quality: int, db: AsyncSession = Depends(get_db)):
    """提交一次复习评分，更新SM-2参数
    quality: 0-5 (0=完全忘记, 3=基本记住, 5=完全掌握)
    """
    if quality < 0 or quality > 5:
        raise HTTPException(status_code=400, detail="quality must be 0-5")

    result = await db.execute(
        select(KnowledgeMastery).where(KnowledgeMastery.id == mastery_id)
    )
    mastery = result.scalar_one_or_none()
    if not mastery:
        raise HTTPException(status_code=404, detail="掌握度记录不存在")

    mastery = sm2_algorithm(mastery, quality)
    await db.commit()

    return APIResponse(data={
        "mastery_id": mastery.id,
        "mastery_level": round(mastery.mastery_level * 100, 1),
        "ease_factor": round(mastery.ease_factor, 2),
        "interval_days": mastery.interval_days,
        "repetitions": mastery.repetitions,
        "next_review_at": mastery.next_review_at.isoformat() if mastery.next_review_at else None,
    })


@router.get("/stats")
async def review_stats(db: AsyncSession = Depends(get_db)):
    """复习统计概览"""
    now = datetime.now()

    # Total knowledge points with mastery
    total_result = await db.execute(select(func.count(KnowledgeMastery.id)))
    total = total_result.scalar()

    # Due now
    due_result = await db.execute(
        select(func.count(KnowledgeMastery.id))
        .where(or_(KnowledgeMastery.next_review_at.is_(None), KnowledgeMastery.next_review_at <= now))
    )
    due_now = due_result.scalar()

    # Average mastery
    avg_result = await db.execute(
        select(func.avg(KnowledgeMastery.mastery_level))
    )
    avg_mastery = round((avg_result.scalar() or 0) * 100, 1)

    # Due today, this week
    week_later = now + timedelta(days=7)
    week_result = await db.execute(
        select(func.count(KnowledgeMastery.id))
        .where(or_(KnowledgeMastery.next_review_at.is_(None), KnowledgeMastery.next_review_at <= week_later))
    )
    due_this_week = week_result.scalar()

    return APIResponse(data={
        "total_knowledge_points": total,
        "average_mastery": avg_mastery,
        "due_now": due_now,
        "due_this_week": due_this_week,
        "message": f"当前有 {due_now} 个知识点需要复习，本周还有 {due_this_week} 个待复习" if due_now > 0 else "暂无到期复习任务，继续保持！",
    })
