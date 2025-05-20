import time
from fastapi import APIRouter, Depends, File, HTTPException,BackgroundTasks, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app import db
from app.core.utils import hash_password
from app.db.database import get_db  # type: ignore
from app.models.user import User  # type: ignore
from app.schemas.user import OTPVerifyRequest, UpdateUser, UserPublic, UserResponse, UserCreate  # type: ignore
from app.crud.user import  get_current_user, get_user_by_username, create_user, get_user_email, get_user_with_follow_counts  # type: ignore
from app.api.auth import otp_storage
from app.utils import otp  # type: ignore
from app.utils import email
from app.media.avatar import save_avatar
from app.schemas.user import UserOut
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/users/{username}", response_model=UserOut)
async def read_user(username: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_with_follow_counts(username, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# It should only be used on a model instance inside a function

@router.get("/{username}", response_model=UserPublic)
async def get_user_profile(username: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserPublic.model_validate(user)



@router.put("/me", response_model=UserPublic)
async def update_profile(
    user_update: UpdateUser,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    current_user.bio = user_update.bio or current_user.bio
    current_user.avatar_url = user_update.avatar_url or current_user.avatar_url

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return UserPublic.model_validate(current_user)



@router.post("/{user_id}/upload-avatar")
async def upload_avatar(
    user_id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
):
    avatar_url = await save_avatar(file, user_id)

    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.avatar_url = avatar_url
    await db.commit()

    return {"message": "Avatar uploaded", "avatar_url": avatar_url}