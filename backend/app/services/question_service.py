from datetime import datetime, timedelta

from sqlalchemy import select, func, distinct as sa_distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.question import Question, QuestionKnowledgePoint
from ..models.knowledge_point import KnowledgePoint
from ..models.knowledge_mastery import KnowledgeMastery
from ..models.practice_record import PracticeRecord


async def get_questions(
    db: AsyncSession,
    q_type: str | None = None,
    part: str | None = None,
    difficulty: int | None = None,
    knowledge_point_id: int | None = None,
    chapter: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Question], int]:
    query = select(Question).options(selectinload(Question.knowledge_points))
    count_query = select(func.count(sa_distinct(Question.id)))

    if q_type:
        query = query.where(Question.type == q_type)
        count_query = count_query.where(Question.type == q_type)
    if part:
        query = query.where(Question.part == part)
        count_query = count_query.where(Question.part == part)
    if difficulty:
        query = query.where(Question.difficulty == difficulty)
        count_query = count_query.where(Question.difficulty == difficulty)
    if knowledge_point_id:
        query = query.join(Question.knowledge_points).where(
            QuestionKnowledgePoint.knowledge_point_id == knowledge_point_id
        )
        count_query = count_query.join(Question.knowledge_points).where(
            QuestionKnowledgePoint.knowledge_point_id == knowledge_point_id
        )
    if chapter:
        query = query.join(Question.knowledge_points).join(
            QuestionKnowledgePoint.knowledge_point
        ).where(KnowledgePoint.chapter == chapter).distinct()
        count_query = count_query.join(Question.knowledge_points).join(
            QuestionKnowledgePoint.knowledge_point
        ).where(KnowledgePoint.chapter == chapter)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size).order_by(Question.id)
    result = await db.execute(query)
    questions = result.scalars().all()

    return list(questions), total


async def get_question(db: AsyncSession, q_id: int) -> Question | None:
    result = await db.execute(
        select(Question)
        .options(selectinload(Question.knowledge_points))
        .where(Question.id == q_id)
    )
    return result.scalar_one_or_none()


async def get_random_questions(
    db: AsyncSession,
    count: int = 10,
    q_type: str | None = None,
    part: str | None = None,
    difficulty: int | None = None,
    knowledge_point_ids: list[int] | None = None,
    chapter: str | None = None,
) -> list[Question]:
    query = select(Question).options(selectinload(Question.knowledge_points))

    if q_type:
        query = query.where(Question.type == q_type)
    if part:
        query = query.where(Question.part == part)
    if difficulty:
        query = query.where(Question.difficulty == difficulty)
    if knowledge_point_ids:
        query = query.join(Question.knowledge_points).where(
            QuestionKnowledgePoint.knowledge_point_id.in_(knowledge_point_ids)
        )
    if chapter:
        query = query.join(Question.knowledge_points).join(
            QuestionKnowledgePoint.knowledge_point
        ).where(KnowledgePoint.chapter == chapter).distinct()

    query = query.order_by(func.random()).limit(count)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_question(db: AsyncSession, data: dict) -> Question:
    kp_ids = data.pop("knowledge_point_ids", [])
    question = Question(**data)
    db.add(question)
    await db.flush()

    for kp_id in kp_ids:
        db.add(QuestionKnowledgePoint(question_id=question.id, knowledge_point_id=kp_id))

    await db.commit()
    created = await get_question(db, question.id)
    assert created is not None
    return created


def _normalize(s: str) -> str:
    """Normalize answer for comparison: strip whitespace, remove extra spaces"""
    return ' '.join(s.strip().split())


def _check_answer(question_type: str, user_answer: str, correct_answer: str) -> tuple[bool, float]:
    """Check answer with type-specific logic. Returns (is_correct, score_ratio)."""
    ua = _normalize(user_answer)
    ca = _normalize(correct_answer)

    if not ua:
        return False, 0.0

    if question_type == 'multi_choice':
        # Multi-choice: compare sorted answer letters (e.g., "A,C,D" vs "ACD")
        user_set = set(ua.upper().replace(',', '').replace(' ', ''))
        correct_set = set(ca.upper().replace(',', '').replace(' ', ''))
        if user_set == correct_set:
            return True, 1.0
        elif user_set.issubset(correct_set) and len(user_set) >= len(correct_set) * 0.5:
            # Partial: got at least half correct options, no wrong ones
            return False, 0.5
        return False, 0.0

    elif question_type in ('fill_blank', 'short_answer'):
        # Support multiple acceptable answers separated by ||
        acceptable = [a.strip() for a in ca.split('||')]
        for acc in acceptable:
            if _normalize(acc).upper() == ua.upper():
                return True, 1.0
            # Also check if user answer contains the key answer
            if len(ua) >= 3 and _normalize(acc).upper() in ua.upper():
                return True, 0.8
        return False, 0.0

    elif question_type == 'programming':
        # For programming: normalize code (remove extra whitespace, normalize newlines)
        ua_norm = ua.replace(' ', '').replace('\n', '').replace('\r', '')
        ca_norm = ca.replace(' ', '').replace('\n', '').replace('\r', '')
        if ua_norm == ca_norm:
            return True, 1.0
        # Check if key logic elements exist
        return False, 0.0

    else:
        # single_choice, program_reading, analysis, calculation
        return ua.upper() == ca.upper(), 1.0 if ua.upper() == ca.upper() else 0.0


def _quality_from_score(is_correct: bool, score_ratio: float) -> int:
    if is_correct:
        return 5
    if score_ratio >= 0.5:
        return 3
    return 1


async def _update_mastery_from_practice(
    db: AsyncSession,
    question: Question,
    is_correct: bool,
    score_ratio: float,
    user_id: int | None = None,
) -> None:
    quality = _quality_from_score(is_correct, score_ratio)
    now = datetime.now()

    for link in question.knowledge_points:
        result = await db.execute(
            select(KnowledgeMastery).where(
                KnowledgeMastery.knowledge_point_id == link.knowledge_point_id,
                KnowledgeMastery.user_id == user_id,
            )
        )
        mastery = result.scalar_one_or_none()

        if mastery is None:
            mastery = KnowledgeMastery(
                user_id=user_id,
                knowledge_point_id=link.knowledge_point_id,
                mastery_level=0.0,
                ease_factor=2.5,
                interval_days=0,
                repetitions=0,
                total_attempts=0,
                correct_attempts=0,
            )
            db.add(mastery)

        mastery.mastery_level = mastery.mastery_level or 0.0
        mastery.ease_factor = mastery.ease_factor or 2.5
        mastery.interval_days = mastery.interval_days or 0
        mastery.repetitions = mastery.repetitions or 0
        mastery.total_attempts = mastery.total_attempts or 0
        mastery.correct_attempts = mastery.correct_attempts or 0

        mastery.total_attempts += 1
        if is_correct:
            mastery.correct_attempts += 1

        practice_signal = quality / 5.0
        mastery.mastery_level = max(
            0.0,
            min(1.0, mastery.mastery_level * 0.72 + practice_signal * 0.28),
        )

        if quality >= 3:
            if mastery.repetitions == 0:
                mastery.interval_days = 1
            elif mastery.repetitions == 1:
                mastery.interval_days = 3
            else:
                mastery.interval_days = max(1, round(mastery.interval_days * mastery.ease_factor))
            mastery.repetitions += 1
        else:
            mastery.repetitions = 0
            mastery.interval_days = 1

        mastery.ease_factor = max(
            1.3,
            mastery.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)),
        )
        mastery.last_reviewed_at = now
        mastery.next_review_at = now + timedelta(days=mastery.interval_days)


async def submit_practice(db: AsyncSession, data: dict, user_id: int | None = None) -> dict:
    question = await get_question(db, data["question_id"])
    if not question:
        return None

    is_correct, score_ratio = _check_answer(
        question.type,
        data["user_answer"],
        question.answer,
    )

    record = PracticeRecord(user_id=user_id, 
        question_id=data["question_id"],
        user_answer=data["user_answer"],
        is_correct=is_correct,
        time_spent=data.get("time_spent", 0),
        practice_mode=data.get("practice_mode", "random"),
    )
    db.add(record)
    await _update_mastery_from_practice(db, question, is_correct, score_ratio, user_id=user_id)
    await db.commit()

    return {
        "is_correct": is_correct,
        "correct_answer": question.answer,
        "explanation": question.explanation or "",
        "score_ratio": score_ratio,
        "knowledge_point_ids": [kp.knowledge_point_id for kp in question.knowledge_points],
    }


async def get_practice_history(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    mode: str | None = None,
    user_id: int | None = None,
) -> tuple[list, int]:
    query = select(PracticeRecord).options(
        selectinload(PracticeRecord.question)
    )
    count_query = select(func.count(PracticeRecord.id))

    if user_id:
        query = query.where(PracticeRecord.user_id == user_id)
        count_query = count_query.where(PracticeRecord.user_id == user_id)
    if mode:
        query = query.where(PracticeRecord.practice_mode == mode)
        count_query = count_query.where(PracticeRecord.practice_mode == mode)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(PracticeRecord.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    records = result.scalars().all()

    return list(records), total


async def get_wrong_question_ids(db: AsyncSession, limit: int = 50, user_id: int | None = None) -> list[int]:
    """Get question IDs the user got wrong, most recent first"""
    result = await db.execute(
        select(PracticeRecord.question_id)
        .where(PracticeRecord.is_correct == False, PracticeRecord.user_id == user_id)
        .order_by(PracticeRecord.created_at.desc())
        .limit(limit)
    )
    return [r[0] for r in result.all()]


async def get_questions_by_ids(db: AsyncSession, ids: list[int]) -> list[Question]:
    result = await db.execute(
        select(Question)
        .options(selectinload(Question.knowledge_points))
        .where(Question.id.in_(ids))
    )
    return list(result.scalars().all())


def question_to_dict(q: Question) -> dict:
    return {
        "id": q.id,
        "type": q.type,
        "part": q.part,
        "difficulty": q.difficulty,
        "content": q.content,
        "options": q.options,
        "answer": q.answer,
        "explanation": q.explanation or "",
        "source": q.source,
        "code_snippet": q.code_snippet,
        "knowledge_point_ids": [kp.knowledge_point_id for kp in q.knowledge_points],
    }


async def get_chapter_summary(db: AsyncSession) -> list[dict]:
    # Get chapter-level KPs (parent is a part node with chapter="")
    from sqlalchemy.orm import aliased
    ParentKP = aliased(KnowledgePoint)
    chapter_info_result = await db.execute(
        select(
            KnowledgePoint.part,
            KnowledgePoint.chapter,
            KnowledgePoint.name.label("chapter_name"),
        )
        .join(ParentKP, KnowledgePoint.parent_id == ParentKP.id)
        .where(KnowledgePoint.chapter != "")
        .where(ParentKP.chapter == "")
    )
    chapter_names = {}
    for row in chapter_info_result.all():
        key = (row.part, row.chapter)
        if key not in chapter_names:
            chapter_names[key] = row.chapter_name

    result = await db.execute(
        select(
            KnowledgePoint.part,
            KnowledgePoint.chapter,
            func.count(sa_distinct(Question.id)).label("question_count")
        )
        .select_from(Question)
        .join(Question.knowledge_points)
        .join(QuestionKnowledgePoint.knowledge_point)
        .where(KnowledgePoint.chapter != "")
        .group_by(KnowledgePoint.part, KnowledgePoint.chapter)
        .order_by(KnowledgePoint.part, KnowledgePoint.chapter)
    )
    return [
        {
            "part": row.part,
            "chapter": row.chapter,
            "chapter_name": chapter_names.get((row.part, row.chapter), row.chapter),
            "question_count": row.question_count,
        }
        for row in result.all()
    ]
