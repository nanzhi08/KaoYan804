from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
import random

from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..schemas.common import APIResponse
from ..models.mock_exam import MockExam
from ..models.question import Question

router = APIRouter(prefix="/api/exam", tags=["模拟考试"])


@router.post("/generate")
async def generate_exam(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    c_total = await db.execute(select(func.count(Question.id)).where(Question.part == "C_programming"))
    ds_total = await db.execute(select(func.count(Question.id)).where(Question.part == "data_structure"))
    c_count = c_total.scalar(); ds_count = ds_total.scalar()
    if c_count < 10 or ds_count < 10:
        raise HTTPException(status_code=400, detail="题库题目不足，无法组卷")

    ds_mc = (await db.execute(select(Question).where(Question.part == "data_structure", Question.type == "single_choice").order_by(func.random()).limit(10))).scalars().all()
    ds_calc = (await db.execute(select(Question).where(Question.part == "data_structure", Question.type == "calculation").order_by(func.random()).limit(1))).scalars().all()
    ds_analysis = (await db.execute(select(Question).where(Question.part == "data_structure", Question.type.in_(["analysis", "short_answer"])).order_by(func.random()).limit(2))).scalars().all()
    ds_prog = (await db.execute(select(Question).where(Question.part == "data_structure", Question.type == "programming").order_by(func.random()).limit(1))).scalars().all()
    c_mc = (await db.execute(select(Question).where(Question.part == "C_programming", Question.type == "single_choice").order_by(func.random()).limit(10))).scalars().all()
    c_fill = (await db.execute(select(Question).where(Question.part == "C_programming", Question.type == "fill_blank").order_by(func.random()).limit(3))).scalars().all()
    c_read = (await db.execute(select(Question).where(Question.part == "C_programming", Question.type == "program_reading").order_by(func.random()).limit(3))).scalars().all()
    c_prog = (await db.execute(select(Question).where(Question.part == "C_programming", Question.type == "programming").order_by(func.random()).limit(3))).scalars().all()

    sections = [
        ("DS MC", ds_mc, 10), ("DS Calc", ds_calc, 1), ("DS Analysis", ds_analysis, 2), ("DS Prog", ds_prog, 1),
        ("C MC", c_mc, 10), ("C Fill", c_fill, 3), ("C Reading", c_read, 3), ("C Prog", c_prog, 3),
    ]
    missing = [f"{l} need {e}, got {len(i)}" for l,i,e in sections if len(i) < e]
    if missing:
        raise HTTPException(status_code=400, detail="组卷失败: " + "; ".join(missing))

    qids = []
    def add(qs, scores):
        for q, s in zip(qs, scores):
            qids.append({"id": q.id, "score": s})
    add(ds_mc, [2]*10); add(ds_calc, [10]); add(ds_analysis, [15,15]); add(ds_prog, [20])
    add(c_mc, [2]*10); add(c_fill, [4,3,3]); add(c_read, [4,3,3]); add(c_prog, [10,10,10])

    exam = MockExam(
        title=f"Mock Exam - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        config={"question_ids": qids, "time_limit": 180},
        total_score=150, user_id=current_user.id,
    )
    db.add(exam); await db.commit(); await db.refresh(exam)

    q_result = await db.execute(select(Question).where(Question.id.in_([qi["id"] for qi in qids])))
    questions = {q.id: q for q in q_result.scalars().all()}
    return APIResponse(data={
        "id": exam.id, "title": exam.title, "total_score": 150, "time_limit": 180,
        "questions": [{"id": qi["id"], "score": qi["score"], "type": questions[qi["id"]].type if qi["id"] in questions else "unknown", "content": questions[qi["id"]].content if qi["id"] in questions else "", "options": questions[qi["id"]].options if qi["id"] in questions else None, "code_snippet": questions[qi["id"]].code_snippet if qi["id"] in questions else None} for qi in qids if qi["id"] in questions],
    })


@router.get("/{exam_id}")
async def get_exam(exam_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(MockExam).where(MockExam.id == exam_id, MockExam.user_id == current_user.id))
    exam = result.scalar_one_or_none()
    if not exam: raise HTTPException(status_code=404, detail="试卷不存在")
    q_ids = [q["id"] for q in exam.config.get("question_ids", [])]
    qs = {}
    if q_ids:
        q_result = await db.execute(select(Question).where(Question.id.in_(q_ids)))
        qs = {q.id: q for q in q_result.scalars().all()}
    show_answer = exam.status == "completed"
    return APIResponse(data={
        "id": exam.id, "title": exam.title, "config": exam.config,
        "score": exam.score, "total_score": exam.total_score,
        "time_taken": exam.time_taken, "answers": exam.answers, "status": exam.status,
        "started_at": exam.started_at.isoformat() if exam.started_at else None,
        "completed_at": exam.completed_at.isoformat() if exam.completed_at else None,
        "created_at": exam.created_at.isoformat() if exam.created_at else None,
        "questions": [{"id": qi["id"], "score": qi["score"], "type": qs[qi["id"]].type if qi["id"] in qs else "unknown", "content": qs[qi["id"]].content if qi["id"] in qs else "", "answer": qs[qi["id"]].answer if qi["id"] in qs and show_answer else None, "explanation": qs[qi["id"]].explanation if qi["id"] in qs and show_answer else None} for qi in exam.config.get("question_ids", []) if qi["id"] in qs],
    })


@router.post("/{exam_id}/start")
async def start_exam(exam_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(MockExam).where(MockExam.id == exam_id, MockExam.user_id == current_user.id))
    exam = result.scalar_one_or_none()
    if not exam: raise HTTPException(status_code=404, detail="试卷不存在")
    if exam.status != "pending": raise HTTPException(status_code=400, detail="考试已开始或已完成")
    exam.status = "in_progress"; exam.started_at = datetime.now(); await db.commit()
    return APIResponse(data={"status": "in_progress"})


@router.post("/{exam_id}/submit")
async def submit_exam(exam_id: int, answers: dict, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(MockExam).where(MockExam.id == exam_id, MockExam.user_id == current_user.id))
    exam = result.scalar_one_or_none()
    if not exam: raise HTTPException(status_code=404, detail="试卷不存在")
    q_ids = [q["id"] for q in exam.config.get("question_ids", [])]
    q_result = await db.execute(select(Question).where(Question.id.in_(q_ids)))
    questions = {q.id: q for q in q_result.scalars().all()}
    total = 0; scored = []
    for qi in exam.config.get("question_ids", []):
        q = questions.get(qi["id"])
        ua = answers.get(str(qi["id"]), "")
        if q:
            correct = ua.strip().upper() == q.answer.strip().upper()
            earned = qi["score"] if correct else 0; total += earned
            scored.append({"question_id": qi["id"], "user_answer": ua, "correct_answer": q.answer, "is_correct": correct, "score": earned, "max_score": qi["score"]})
    now = datetime.now()
    exam.score = total; exam.answers = scored; exam.status = "completed"; exam.completed_at = now
    if exam.started_at: exam.time_taken = int((now - exam.started_at).total_seconds())
    await db.commit()
    return APIResponse(data={"score": total, "total_score": exam.total_score, "accuracy": round(total / exam.total_score * 100, 1) if exam.total_score > 0 else 0, "answers": scored, "time_taken": exam.time_taken})


@router.get("")
async def list_exams(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(MockExam).where(MockExam.user_id == current_user.id).order_by(MockExam.created_at.desc()).limit(20))
    exams = result.scalars().all()
    return APIResponse(data=[{"id": e.id, "title": e.title, "score": e.score, "total_score": e.total_score, "status": e.status, "time_taken": e.time_taken, "created_at": e.created_at.isoformat() if e.created_at else None} for e in exams])
