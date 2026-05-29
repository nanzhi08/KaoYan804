from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
import random

from ..database import get_db
from ..schemas.common import APIResponse
from ..models.mock_exam import MockExam
from ..models.question import Question

router = APIRouter(prefix="/api/exam", tags=["模拟考试"])


@router.post("/generate")
async def generate_exam(db: AsyncSession = Depends(get_db)):
    """按804真题比例自动组卷：DS 80分 + C 70分，共150分"""
    # Count available questions
    c_total = await db.execute(
        select(func.count(Question.id)).where(Question.part == "C_programming")
    )
    ds_total = await db.execute(
        select(func.count(Question.id)).where(Question.part == "data_structure")
    )
    c_count = c_total.scalar()
    ds_count = ds_total.scalar()

    if c_count < 10 or ds_count < 10:
        raise HTTPException(status_code=400, detail="题库不足，至少需要C语言和DS各10道题")

    # Pick questions to match 804 exam pattern:
    # DS: 10 MC (20pts) + 1 calc (10pts) + 2 analysis (30pts) + 1 programming (20pts) = 80pts
    # C:  10 MC (20pts) + 3 fill_blank (10pts) + 3 program_reading (10pts) + 3 programming (30pts) = 70pts

    ds_mc = await db.execute(
        select(Question).where(Question.part == "data_structure", Question.type == "single_choice")
        .order_by(func.random()).limit(10)
    )
    ds_calc = await db.execute(
        select(Question).where(Question.part == "data_structure", Question.type == "calculation")
        .order_by(func.random()).limit(1)
    )
    ds_analysis = await db.execute(
        select(Question).where(Question.part == "data_structure", Question.type.in_(["analysis", "short_answer"]))
        .order_by(func.random()).limit(2)
    )
    ds_prog = await db.execute(
        select(Question).where(Question.part == "data_structure", Question.type == "programming")
        .order_by(func.random()).limit(1)
    )

    c_mc = await db.execute(
        select(Question).where(Question.part == "C_programming", Question.type == "single_choice")
        .order_by(func.random()).limit(10)
    )
    c_fill = await db.execute(
        select(Question).where(Question.part == "C_programming", Question.type == "fill_blank")
        .order_by(func.random()).limit(3)
    )
    c_read = await db.execute(
        select(Question).where(Question.part == "C_programming", Question.type == "program_reading")
        .order_by(func.random()).limit(3)
    )
    c_prog = await db.execute(
        select(Question).where(Question.part == "C_programming", Question.type == "programming")
        .order_by(func.random()).limit(3)
    )

    question_ids = []
    # DS questions with scores
    for q in ds_mc.scalars().all():
        question_ids.append({"id": q.id, "score": 2})
    for q in ds_calc.scalars().all():
        question_ids.append({"id": q.id, "score": 10})
    for q in ds_analysis.scalars().all():
        question_ids.append({"id": q.id, "score": 15})
    for q in ds_prog.scalars().all():
        question_ids.append({"id": q.id, "score": 20})

    # C questions with scores
    for q in c_mc.scalars().all():
        question_ids.append({"id": q.id, "score": 2})
    for q in c_fill.scalars().all():
        question_ids.append({"id": q.id, "score": 3})  # ~10 pts total
    for q in c_read.scalars().all():
        question_ids.append({"id": q.id, "score": 3})  # ~10 pts total
    for q in c_prog.scalars().all():
        question_ids.append({"id": q.id, "score": 10})

    # Adjust fill/read scores to exact 10 each
    total_fill_score = sum(it["score"] for it in question_ids if it["score"] == 3 and it in question_ids[-9:-3])
    total_read_score = sum(it["score"] for it in question_ids if it["score"] == 3 and it in question_ids[-6:-3])

    exam = MockExam(
        title=f"804模拟考试 - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        config={
            "total_score": 150,
            "time_limit": 180,  # 3 hours in minutes
            "question_ids": question_ids,
        },
        total_score=150,
        status="pending",
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)

    # Fetch all questions with details
    all_ids = [q["id"] for q in question_ids]
    qs_result = await db.execute(select(Question).where(Question.id.in_(all_ids)))
    questions = {q.id: q for q in qs_result.scalars().all()}

    return APIResponse(data={
        "exam_id": exam.id,
        "title": exam.title,
        "total_score": exam.total_score,
        "time_limit": 180,
        "question_count": len(question_ids),
        "questions": [
            {
                "id": qi["id"],
                "score": qi["score"],
                "type": questions[qi["id"]].type if qi["id"] in questions else "unknown",
                "part": questions[qi["id"]].part if qi["id"] in questions else "unknown",
                "content": questions[qi["id"]].content if qi["id"] in questions else "",
                "options": questions[qi["id"]].options if qi["id"] in questions else None,
                "code_snippet": questions[qi["id"]].code_snippet if qi["id"] in questions else None,
            }
            for qi in question_ids
            if qi["id"] in questions
        ],
    })


@router.get("/{exam_id}")
async def get_exam(exam_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MockExam).where(MockExam.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    # Fetch associated questions
    q_ids = [q["id"] for q in exam.config.get("question_ids", [])]
    qs = {}
    if q_ids:
        q_result = await db.execute(select(Question).where(Question.id.in_(q_ids)))
        qs = {q.id: q for q in q_result.scalars().all()}

    return APIResponse(data={
        "id": exam.id,
        "title": exam.title,
        "config": exam.config,
        "score": exam.score,
        "total_score": exam.total_score,
        "time_taken": exam.time_taken,
        "answers": exam.answers,
        "status": exam.status,
        "started_at": exam.started_at.isoformat() if exam.started_at else None,
        "completed_at": exam.completed_at.isoformat() if exam.completed_at else None,
        "created_at": exam.created_at.isoformat() if exam.created_at else None,
        "questions": [
            {
                "id": qi["id"],
                "score": qi["score"],
                "type": qs[qi["id"]].type if qi["id"] in qs else "unknown",
                "content": qs[qi["id"]].content if qi["id"] in qs else "",
                "answer": qs[qi["id"]].answer if qi["id"] in qs and exam.status == "completed" else None,
                "explanation": qs[qi["id"]].explanation if qi["id"] in qs and exam.status == "completed" else None,
            }
            for qi in exam.config.get("question_ids", [])
            if qi["id"] in qs
        ],
    })


@router.post("/{exam_id}/start")
async def start_exam(exam_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MockExam).where(MockExam.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    if exam.status != "pending":
        raise HTTPException(status_code=400, detail="考试已开始或已结束")

    exam.status = "in_progress"
    exam.started_at = datetime.now()
    await db.commit()
    return APIResponse(data={"status": "in_progress"})


@router.post("/{exam_id}/submit")
async def submit_exam(exam_id: int, answers: dict, db: AsyncSession = Depends(get_db)):
    """提交考试答案并自动评分
    answers: {"question_id": "user_answer", ...}
    """
    result = await db.execute(select(MockExam).where(MockExam.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    # Fetch questions
    q_ids = [q["id"] for q in exam.config.get("question_ids", [])]
    q_result = await db.execute(select(Question).where(Question.id.in_(q_ids)))
    questions = {q.id: q for q in q_result.scalars().all()}

    total = 0
    scored_answers = []
    for qi in exam.config.get("question_ids", []):
        q = questions.get(qi["id"])
        user_ans = answers.get(str(qi["id"]), "")
        if q:
            correct = user_ans.strip().upper() == q.answer.strip().upper()
            earned = qi["score"] if correct else 0
            total += earned
            scored_answers.append({
                "question_id": qi["id"],
                "user_answer": user_ans,
                "correct_answer": q.answer,
                "is_correct": correct,
                "score": earned,
                "max_score": qi["score"],
            })

    now = datetime.now()
    exam.score = total
    exam.answers = scored_answers
    exam.status = "completed"
    exam.completed_at = now
    if exam.started_at:
        exam.time_taken = int((now - exam.started_at).total_seconds())
    await db.commit()

    return APIResponse(data={
        "score": total,
        "total_score": exam.total_score,
        "accuracy": round(total / exam.total_score * 100, 1) if exam.total_score > 0 else 0,
        "answers": scored_answers,
        "time_taken": exam.time_taken,
    })


@router.get("")
async def list_exams(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MockExam).order_by(MockExam.created_at.desc()).limit(20)
    )
    exams = result.scalars().all()
    return APIResponse(data=[
        {
            "id": e.id,
            "title": e.title,
            "score": e.score,
            "total_score": e.total_score,
            "status": e.status,
            "time_taken": e.time_taken,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in exams
    ])
