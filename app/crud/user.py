import logging
from fastapi import Depends, HTTPException, status 
from jose import JWTError
import jwt
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app import models
from app.core.utils import SECRET_KEY, hash_password, verify_jwt_token, verify_password # type: ignore
from app.db.database import get_db # type: ignore
from app.models.follow import Follow
from app.schemas.user import UserCreate # type: ignore
from jwt import PyJWTError
import app.models.user as models # type: ignore
from app.utils.hashing import get_password_hash # type: ignore
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.future import select
from app.models.user import User
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
  
#get user by email
async def get_user_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()
#create new user 
async def create_user(db: AsyncSession, user: UserCreate):
    # Hash password as you did before
    hashed_password = hash_password(user.password) 

    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        bio=user.bio,
        avatar_url=user.avatar_url,
        is_active=True
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


#authernicate user
async def authenticate_user(db: AsyncSession, email: str, password: str):
    email = email.strip().lower()  # Normalize email
    result = await db.execute(select(models.User).filter(models.User.email == email))
    user = result.scalars().first()

    if not user:
        print(f"User with email {email} not found")
        return None

    print(f"Found user: {user.username}, verifying password...")

    if verify_password(password, user.hashed_password):
        print("Password verified successfully")
        return user
    else:
        print("Password verification failed")
        return None



async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalar_one_or_none()


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> models.User:
    logging.debug(f"Received token: {token}")
    try:
        user_id = verify_jwt_token(token)
    except HTTPException as e:
        logging.error(f"Token verification failed: {e.detail}")
        raise e

    logging.debug(f"Decoded user_id: {user_id}")
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        logging.error("User not found in database.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user

async def get_user_with_follow_counts(username: str, db: AsyncSession):
    # Fetch user
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        return None

    # Count followers
    followers_count_query = select(func.count()).select_from(Follow).where(Follow.followee_id == user.id)
    result = await db.execute(followers_count_query)
    followers_count = result.scalar() or 0

    # Count following
    following_count_query = select(func.count()).select_from(Follow).where(Follow.follower_id == user.id)
    result = await db.execute(following_count_query)
    following_count = result.scalar() or 0

    # Add counts to user object dynamically (or create a dict response)
    user.followers_count = followers_count
    user.following_count = following_count

    return user