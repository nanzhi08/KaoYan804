import json
import uuid
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from sqlalchemy import select

from ..database import get_db
from ..models.knowledge_point import KnowledgePoint
from ..schemas.common import APIResponse
from ..services import ai_service

router = APIRouter(prefix="/api/ai", tags=["AI导师"])


class ChatRequest(BaseModel):
    conversation_id: int | None = None
    provider: str = "deepseek"
    message: str
    knowledge_point_id: int | None = None
    question_id: int | None = None
    messages: list[dict] = []


class FeedbackRequest(BaseModel):
    conversation_id: int
    message_id: str
    message_index: int
    rating: int  # 1 = thumbs up, -1 = thumbs down
    comment: str = ""


@router.get("/conversations")
async def list_conversations(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from ..models.ai_conversation import AIConversation

    result = await db.execute(
        select(AIConversation).order_by(AIConversation.updated_at.desc()).limit(50)
    )
    convs = result.scalars().all()
    return APIResponse(data=[
        {
            "id": c.id,
            "provider": c.provider,
            "model": c.model,
            "title": c.title,
            "message_count": len(c.messages) if c.messages else 0,
            "created_at": c.created_at.isoformat(),
            "updated_at": (c.updated_at or c.created_at).isoformat(),
        }
        for c in convs
    ])


@router.get("/conversations/{conv_id}")
async def get_conversation(conv_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from ..models.ai_conversation import AIConversation

    result = await db.execute(select(AIConversation).where(AIConversation.id == conv_id))
    conv = result.scalar_one_or_none()
    if not conv:
        return APIResponse(code=404, message="对话不存在")
    return APIResponse(data={
        "id": conv.id,
        "provider": conv.provider,
        "model": conv.model,
        "messages": conv.messages or [],
        "knowledge_point_id": conv.knowledge_point_id,
        "question_id": conv.question_id,
    })


@router.post("/chat")
async def chat_with_ai(data: ChatRequest, db: AsyncSession = Depends(get_db)):
    messages = data.messages + [{"role": "user", "content": data.message}]

    async def generate():
        async for chunk, conv in ai_service.chat_stream(
            db, data.provider, messages, data.conversation_id,
            data.knowledge_point_id, data.question_id,
        ):
            yield f"data: {json.dumps({'chunk': chunk, 'conversation_id': conv.id})}\n\n"
        last_id = conv.messages[-1].get("id", "") if conv.messages else ""
        yield f"data: {json.dumps({'done': True, 'conversation_id': conv.id, 'msg_id': last_id})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/explain")
async def explain_knowledge_point(
    kp_id: int = Query(...),
    provider: str = Query("deepseek"),
    db: AsyncSession = Depends(get_db),
):
    prompt = await ai_service.build_explain_prompt(db, kp_id)

    async def generate():
        provider_obj = ai_service.get_provider(provider)
        messages = ai_service._ensure_message_ids([
            {"role": "system", "content": ai_service.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ])
        full_text = ""
        conv = None
        try:
            async for chunk in provider_obj.chat_stream(messages):
                full_text += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            messages.append({
                "role": "assistant", "content": full_text,
                "id": str(uuid.uuid4()),
            })
            conv = await ai_service.get_or_create_conversation(
                db, None, provider, kp_id=kp_id,
                first_user_message=prompt,
            )
            conv.messages = messages
            await db.commit()
            last_id = messages[-1].get("id", "")
            yield f"data: {json.dumps({'done': True, 'conversation_id': conv.id, 'msg_id': last_id})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/explain/save")
async def explain_and_save_knowledge_point(
    kp_id: int = Query(...),
    provider: str = Query("deepseek"),
    db: AsyncSession = Depends(get_db),
):
    kp_result = await db.execute(
        select(KnowledgePoint).where(KnowledgePoint.id == kp_id)
    )
    kp = kp_result.scalar_one_or_none()
    if not kp:
        return APIResponse(code=404, message="知识点不存在")

    prompt = await ai_service.build_explain_prompt(db, kp_id)
    provider_obj = ai_service.get_provider(provider)
    messages = ai_service._ensure_message_ids([
        {"role": "system", "content": ai_service.SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])
    full_text = await provider_obj.chat(messages)

    kp.ai_explanation = full_text
    await db.commit()

    return APIResponse(data={
        "kp_id": kp_id,
        "ai_explanation": full_text,
    })


@router.post("/explain/save-stream")
async def explain_and_save_stream(
    kp_id: int = Query(...),
    provider: str = Query("deepseek"),
    db: AsyncSession = Depends(get_db),
):
    prompt = await ai_service.build_explain_prompt(db, kp_id)

    async def generate():
        provider_obj = ai_service.get_provider(provider)
        messages = ai_service._ensure_message_ids([
            {"role": "system", "content": ai_service.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ])
        full_text = ""
        try:
            async for chunk in provider_obj.chat_stream(messages):
                full_text += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            kp_result = await db.execute(
                select(KnowledgePoint).where(KnowledgePoint.id == kp_id)
            )
            kp = kp_result.scalar_one_or_none()
            if kp:
                kp.ai_explanation = full_text
                await db.commit()
            yield f"data: {json.dumps({'done': True, 'kp_id': kp_id})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/explain/batch")
async def batch_explain_all_leaf_knowledge_points(
    provider: str = Query("deepseek"),
    db: AsyncSession = Depends(get_db),
):
    all_kps_result = await db.execute(select(KnowledgePoint.id))
    all_ids = set(r[0] for r in all_kps_result.all())

    parent_ids_result = await db.execute(
        select(KnowledgePoint.parent_id).where(
            KnowledgePoint.parent_id.isnot(None)
        ).distinct()
    )
    parent_ids = set(r[0] for r in parent_ids_result.all())

    already_cached_result = await db.execute(
        select(KnowledgePoint.id).where(
            KnowledgePoint.ai_explanation.isnot(None),
            KnowledgePoint.ai_explanation != "",
        )
    )
    already_cached_ids = set(r[0] for r in already_cached_result.all())

    leaf_ids = sorted(all_ids - parent_ids - already_cached_ids)

    provider_obj = ai_service.get_provider(provider)
    generated = 0
    errors = []

    for kp_id in leaf_ids:
        try:
            kp_result = await db.execute(
                select(KnowledgePoint).where(KnowledgePoint.id == kp_id)
            )
            kp = kp_result.scalar_one_or_none()
            if not kp:
                continue

            prompt = await ai_service.build_explain_prompt(db, kp_id)
            messages = ai_service._ensure_message_ids([
                {"role": "system", "content": ai_service.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ])
            full_text = await provider_obj.chat(messages)

            kp.ai_explanation = full_text
            await db.commit()
            generated += 1
        except Exception as e:
            errors.append({"kp_id": kp_id, "error": str(e)})
            await db.rollback()

    return APIResponse(data={
        "total_leaves": len(leaf_ids),
        "skipped_cached": len(already_cached_ids),
        "generated": generated,
        "errors": errors,
    })


@router.post("/review-answer")
async def review_answer(
    question_id: int = Query(...),
    user_answer: str = Query(""),
    provider: str = Query("deepseek"),
    db: AsyncSession = Depends(get_db),
):
    prompt = await ai_service.build_review_prompt(db, question_id, user_answer)

    async def generate():
        provider_obj = ai_service.get_provider(provider)
        messages = ai_service._ensure_message_ids([
            {"role": "system", "content": ai_service.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ])
        full_text = ""
        try:
            async for chunk in provider_obj.chat_stream(messages):
                full_text += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            messages.append({
                "role": "assistant", "content": full_text,
                "id": str(uuid.uuid4()),
            })
            conv = await ai_service.get_or_create_conversation(
                db, None, provider, question_id=question_id,
            )
            conv.messages = messages
            await db.commit()
            last_id = messages[-1].get("id", "")
            yield f"data: {json.dumps({'done': True, 'conversation_id': conv.id, 'msg_id': last_id})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from ..models.ai_conversation import AIConversation

    result = await db.execute(select(AIConversation).where(AIConversation.id == conv_id))
    conv = result.scalar_one_or_none()
    if not conv:
        return APIResponse(code=404, message="对话不存在")
    await db.delete(conv)
    await db.commit()
    return APIResponse(message="删除成功")


@router.post("/feedback")
async def submit_feedback(data: FeedbackRequest, db: AsyncSession = Depends(get_db)):
    from ..services.feedback_service import save_feedback_and_extract_example

    feedback, example = await save_feedback_and_extract_example(db, data)
    result = {
        "feedback_id": feedback.id,
        "training_example_created": example is not None,
    }
    if example:
        result["training_example_id"] = example.id
    return APIResponse(data=result)


@router.get("/training-examples")
async def list_training_examples(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select, func
    from ..models.ai_training_example import AITrainingExample

    q = select(AITrainingExample)
    if is_active is not None:
        q = q.where(AITrainingExample.is_active == is_active)
    q = q.order_by(AITrainingExample.created_at.desc())

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar()

    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    examples = result.scalars().all()

    return APIResponse(data={
        "items": [
            {
                "id": e.id,
                "user_question": e.user_question[:200],
                "assistant_answer": e.assistant_answer[:200],
                "chapter": e.chapter,
                "part": e.part,
                "keywords": e.keywords,
                "usage_count": e.usage_count,
                "is_active": e.is_active,
                "created_at": e.created_at.isoformat(),
            }
            for e in examples
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.delete("/training-examples/{example_id}")
async def delete_training_example(example_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from ..models.ai_training_example import AITrainingExample

    result = await db.execute(
        select(AITrainingExample).where(AITrainingExample.id == example_id)
    )
    example = result.scalar_one_or_none()
    if not example:
        return APIResponse(code=404, message="训练示例不存在")
    example.is_active = False
    await db.commit()
    return APIResponse(message="已停用")


@router.patch("/training-examples/{example_id}")
async def toggle_training_example(
    example_id: int,
    is_active: bool = Query(...),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from ..models.ai_training_example import AITrainingExample

    result = await db.execute(
        select(AITrainingExample).where(AITrainingExample.id == example_id)
    )
    example = result.scalar_one_or_none()
    if not example:
        return APIResponse(code=404, message="训练示例不存在")
    example.is_active = is_active
    await db.commit()
    return APIResponse(message="更新成功")
