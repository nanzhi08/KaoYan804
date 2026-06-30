from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies import (
    get_current_user, hash_password, verify_password, create_access_token,
)
from ..models.user import User
from ..models.invite_code import InviteCode
from ..schemas.common import APIResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    invite_code: str


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        return APIResponse(code=401, message="Invalid username or password")

    token = create_access_token({"user_id": str(user.id), "role": user.role})
    return APIResponse(data={
        "access_token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
    })


@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    code_result = await db.execute(
        select(InviteCode).where(
            InviteCode.code == data.invite_code,
            InviteCode.is_used == False,
        )
    )
    invite = code_result.scalar_one_or_none()
    if not invite:
        return APIResponse(code=400, message="Invalid or already used invite code")

    existing = await db.execute(select(User).where(User.username == data.username))
    if existing.scalar_one_or_none():
        return APIResponse(code=409, message="Username already exists")

    if len(data.password) < 6:
        return APIResponse(code=400, message="Password must be at least 6 characters")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        role="user",
    )
    db.add(user)
    await db.flush()

    invite.is_used = True
    invite.used_by = user.id
    await db.commit()

    token = create_access_token({"user_id": str(user.id), "role": user.role})
    return APIResponse(data={
        "access_token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
    })


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return APIResponse(data={
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    })
