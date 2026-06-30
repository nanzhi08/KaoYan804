import json
import uuid
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from sqlalchemy import select

from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..models.knowledge_point import KnowledgePoint
from ..schemas.common import APIResponse
from ..services import ai_service

router = APIRouter(prefix="/api/ai", tags=["AI??"])


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
    rating: int
    comment: str = ""


@router.get("/conversations")
async def list_conversations(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    from ..models.ai_conversation import AIConversation
    result = await db.execute(
        select(AIConversation).where(AIConversation.user_id == current_user.id)
        .order_by(AIConversation.updated_at.desc()).limit(50)
    )
    convs = result.scalars().all()
    return APIResponse(data=[{"id": c.id, "provider": c.provider, "model": c.model, "title": c.title, "message_count": len(c.messages) if c.messages else 0, "created_at": c.created_at.isoformat(), "updated_at": (c.updated_at or c.created_at).isoformat()} for c in convs])


@router.get("/conversations/{conv_id}")
async def get_conversation(conv_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    from ..models.ai_conversation import AIConversation
    result = await db.execute(select(AIConversation).where(AIConversation.id == conv_id, AIConversation.user_id == current_user.id))
    conv = result.scalar_one_or_none()
    if not conv: return APIResponse(code=404, message="conversation not found")
    return APIResponse(data={"id": conv.id, "provider": conv.provider, "model": conv.model, "messages": conv.messages or [], "knowledge_point_id": conv.knowledge_point_id, "question_id": conv.question_id})


@router.post("/chat")
async def chat_with_ai(data: ChatRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    messages = data.messages + [{"role": "user", "content": data.message}]
    async def generate():
        try:
            async for chunk, conv in ai_service.chat_stream(db, data.provider, messages, data.conversation_id, data.knowledge_point_id, data.question_id, user_id=current_user.id):
                yield f"data: {json.dumps({'chunk': chunk, 'conversation_id': conv.id})}\n\n"
            last_id = conv.messages[-1].get("id", "") if conv.messages else ""
            yield f"data: {json.dumps({'done': True, 'conversation_id': conv.id, 'msg_id': last_id})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/explain")
async def explain_knowledge_point(kp_id: int = Query(...), provider: str = Query("deepseek"), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    prompt = await ai_service.build_explain_prompt(db, kp_id)
    async def generate():
        try:
            provider_obj = ai_service.get_provider(provider)
            messages = ai_service._ensure_message_ids([{"role": "system", "content": ai_service.SYSTEM_PROMPT}, {"role": "user", "content": prompt}])
            full_text = ""
            async for chunk in provider_obj.chat_stream(messages):
                full_text += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            messages.append({"role": "assistant", "content": full_text, "id": str(uuid.uuid4())})
            conv = await ai_service.get_or_create_conversation(db, None, provider, kp_id=kp_id, first_user_message=prompt, user_id=current_user.id)
            conv.messages = messages; await db.commit()
            last_id = messages[-1].get("id", "")
            yield f"data: {json.dumps({'done': True, 'conversation_id': conv.id, 'msg_id': last_id})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/explain/save")
async def explain_and_save_knowledge_point(kp_id: int = Query(...), provider: str = Query("deepseek"), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    kp_result = await db.execute(select(KnowledgePoint).where(KnowledgePoint.id == kp_id))
    kp = kp_result.scalar_one_or_none()
    if not kp: return APIResponse(code=404, message="knowledge point not found")
    prompt = await ai_service.build_explain_prompt(db, kp_id)
    provider_obj = ai_service.get_provider(provider)
    messages = ai_service._ensure_message_ids([{"role": "system", "content": ai_service.SYSTEM_PROMPT}, {"role": "user", "content": prompt}])
    full_text = ""
    async for chunk in provider_obj.chat_stream(messages): full_text += chunk
    kp.ai_explanation = full_text; await db.commit()
    return APIResponse(data={"kp_id": kp.id, "ai_explanation": full_text})


@router.post("/explain/batch")
async def batch_explain(provider: str = Query("deepseek"), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    from sqlalchemy import and_
    subq = select(KnowledgePoint.id).where(KnowledgePoint.parent_id.isnot(None))
    leaf_ids_result = await db.execute(subq); leaf_ids = {row[0] for row in leaf_ids_result.all()}
    parent_ids_result = await db.execute(select(KnowledgePoint.parent_id).where(KnowledgePoint.parent_id.isnot(None)).distinct())
    non_leaf_ids = {row[0] for row in parent_ids_result.all() if row[0] is not None}
    true_leaf_ids = leaf_ids - non_leaf_ids
    q = select(KnowledgePoint).where(KnowledgePoint.id.in_(true_leaf_ids), and_(KnowledgePoint.ai_explanation.is_(None) | (KnowledgePoint.ai_explanation == "")))
    result = await db.execute(q); kps = result.scalars().all()
    total_leaves = len(true_leaf_ids); generated = 0; errors = []
    provider_obj = ai_service.get_provider(provider)
    for kp in kps:
        try:
            prompt = await ai_service.build_explain_prompt(db, kp.id)
            messages = ai_service._ensure_message_ids([{"role": "system", "content": ai_service.SYSTEM_PROMPT}, {"role": "user", "content": prompt}])
            full_text = ""
            async for chunk in provider_obj.chat_stream(messages): full_text += chunk
            kp.ai_explanation = full_text; generated += 1; await db.commit()
        except Exception as e: errors.append({"kp_id": kp.id, "name": kp.name, "error": str(e)})
    return APIResponse(data={"total_leaves": total_leaves, "generated": generated, "errors": errors})


@router.post("/review-question")
async def review_question(question_id: int = Query(...), user_answer: str = Query(""), provider: str = Query("deepseek"), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    prompt = await ai_service.build_review_prompt(db, question_id, user_answer)
    async def generate():
        try:
            provider_obj = ai_service.get_provider(provider)
            messages = ai_service._ensure_message_ids([{"role": "system", "content": ai_service.SYSTEM_PROMPT}, {"role": "user", "content": prompt}])
            full_text = ""
            async for chunk in provider_obj.chat_stream(messages):
                full_text += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            messages.append({"role": "assistant", "content": full_text, "id": str(uuid.uuid4())})
            conv = await ai_service.get_or_create_conversation(db, None, provider, question_id=question_id, user_id=current_user.id)
            conv.messages = messages; await db.commit()
            last_id = messages[-1].get("id", "")
            yield f"data: {json.dumps({'done': True, 'conversation_id': conv.id, 'msg_id': last_id})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    from ..models.ai_conversation import AIConversation
    result = await db.execute(select(AIConversation).where(AIConversation.id == conv_id, AIConversation.user_id == current_user.id))
    conv = result.scalar_one_or_none()
    if not conv: return APIResponse(code=404, message="conversation not found")
    await db.delete(conv); await db.commit()
    return APIResponse(message="deleted")


@router.post("/feedback")
async def submit_feedback(data: FeedbackRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    from ..services.feedback_service import save_feedback_and_extract_example
    feedback, example = await save_feedback_and_extract_example(db, data, current_user.id)
    result = {"feedback_id": feedback.id, "training_example_created": example is not None}
    if example: result["training_example_id"] = example.id
    return APIResponse(data=result)


@router.get("/training-examples")
async def list_training_examples(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), is_active: bool | None = Query(None), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    from sqlalchemy import select, func
    from ..models.ai_training_example import AITrainingExample
    q = select(AITrainingExample).where(AITrainingExample.user_id == current_user.id)
    if is_active is not None: q = q.where(AITrainingExample.is_active == is_active)
    q = q.order_by(AITrainingExample.created_at.desc())
    count_q = select(func.count()).select_from(q.subquery()); total = (await db.execute(count_q)).scalar()
    q = q.offset((page - 1) * page_size).limit(page_size); result = await db.execute(q); examples = result.scalars().all()
    return APIResponse(data={"items": [{"id": e.id, "user_question": e.user_question[:200], "assistant_answer": e.assistant_answer[:200], "chapter": e.chapter, "part": e.part, "keywords": e.keywords, "usage_count": e.usage_count, "is_active": e.is_active, "created_at": e.created_at.isoformat()} for e in examples], "total": total, "page": page, "page_size": page_size})


@router.delete("/training-examples/{example_id}")
async def delete_training_example(example_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    from ..models.ai_training_example import AITrainingExample
    result = await db.execute(select(AITrainingExample).where(AITrainingExample.id == example_id, AITrainingExample.user_id == current_user.id))
    example = result.scalar_one_or_none()
    if not example: return APIResponse(code=404, message="training example not found")
    example.is_active = False; await db.commit()
    return APIResponse(message="deactivated")


@router.patch("/training-examples/{example_id}")
async def toggle_training_example(example_id: int, is_active: bool = Query(...), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    from ..models.ai_training_example import AITrainingExample
    result = await db.execute(select(AITrainingExample).where(AITrainingExample.id == example_id, AITrainingExample.user_id == current_user.id))
    example = result.scalar_one_or_none()
    if not example: return APIResponse(code=404, message="training example not found")
    example.is_active = is_active; await db.commit()
    return APIResponse(message="updated")
