import secrets
import string

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import require_admin
from ..models.user import User
from ..models.invite_code import InviteCode
from ..models.practice_record import PracticeRecord
from ..models.ai_conversation import AIConversation
from ..models.ai_feedback import AIFeedback
from ..models.ai_training_example import AITrainingExample
from ..models.mock_exam import MockExam
from ..models.document import Document
from ..models.knowledge_mastery import KnowledgeMastery
from ..schemas.common import APIResponse

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def _generate_invite_code(length: int = 12) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_db), current_admin: User = Depends(require_admin)):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()

    user_data = []
    for user in users:
        practice_count = (await db.execute(
            select(func.count(PracticeRecord.id)).where(PracticeRecord.user_id == user.id)
        )).scalar() or 0
        correct_count = (await db.execute(
            select(func.count(PracticeRecord.id)).where(
                PracticeRecord.user_id == user.id,
                PracticeRecord.is_correct == True,
            )
        )).scalar() or 0
        accuracy = round(correct_count / practice_count * 100, 1) if practice_count > 0 else 0

        user_data.append({
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "practice_count": practice_count,
            "accuracy": accuracy,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        })

    return APIResponse(data=user_data)


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), current_admin: User = Depends(require_admin)):
    if user_id == current_admin.id:
        return APIResponse(code=400, message="Cannot delete yourself")

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        return APIResponse(code=404, message="User not found")

    tables = [PracticeRecord, KnowledgeMastery, AIConversation, AIFeedback,
              AITrainingExample, MockExam, Document]
    for table in tables:
        if hasattr(table, "user_id"):
            await db.execute(delete(table).where(table.user_id == user_id))

    await db.execute(delete(InviteCode).where(InviteCode.used_by == user_id))
    await db.execute(delete(InviteCode).where(InviteCode.created_by == user_id))
    await db.execute(delete(User).where(User.id == user_id))
    await db.commit()

    return APIResponse(message="User deleted")


@router.post("/invite-codes")
async def create_invite_code(db: AsyncSession = Depends(get_db), current_admin: User = Depends(require_admin)):
    code = InviteCode(
        code=_generate_invite_code(),
        created_by=current_admin.id,
    )
    db.add(code)
    await db.commit()
    await db.refresh(code)

    return APIResponse(data={
        "id": code.id,
        "code": code.code,
        "is_used": code.is_used,
        "created_at": code.created_at.isoformat() if code.created_at else None,
    })


@router.get("/invite-codes")
async def list_invite_codes(db: AsyncSession = Depends(get_db), current_admin: User = Depends(require_admin)):
    result = await db.execute(select(InviteCode).order_by(InviteCode.created_at.desc()))
    codes = result.scalars().all()

    return APIResponse(data=[
        {
            "id": c.id,
            "code": c.code,
            "is_used": c.is_used,
            "used_by": c.used_by,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in codes
    ])


@router.delete("/invite-codes/{code_id}")
async def delete_invite_code(code_id: int, db: AsyncSession = Depends(get_db), current_admin: User = Depends(require_admin)):
    result = await db.execute(select(InviteCode).where(InviteCode.id == code_id))
    code = result.scalar_one_or_none()
    if not code:
        return APIResponse(code=404, message="Invite code not found")
    if code.is_used:
        return APIResponse(code=400, message="Cannot delete a used invite code")

    await db.delete(code)
    await db.commit()
    return APIResponse(message="Invite code deleted")
