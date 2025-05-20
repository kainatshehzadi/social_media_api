from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.follow import Follow
from app.models.user import User
from app.schemas.follow import FollowResponse, MessageResponse
from app.schemas.user import UserOut
from app.db.database import get_db
from app.crud.follow import get_follower_count, get_following_count, perform_follow_user, perform_unfollow_user
from app.crud.user import get_current_user

router = APIRouter(prefix="/follows",tags = ["follows"])
@router.post("/{username}",response_model=FollowResponse, status_code=status.HTTP_201_CREATED)
async def follow_user(
    username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get the followee user by username
    result = await db.execute(
        select(User).where(User.username == username)
    )
    followee = result.scalar_one_or_none()

    if not followee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User to follow not found."
        )

    return await perform_follow_user(
        follower_id=current_user.id,
        followee_id=followee.id,
        db=db
    )


@router.delete("/{username}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def unfollow_user(
    username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get the followee user by username
    result = await db.execute(
        select(User).where(User.username == username)
    )
    followee = result.scalar_one_or_none()

    if not followee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User to unfollow not found."
        )

    await perform_unfollow_user(
        follower_id=current_user.id,
        followee_id=followee.id,
        db=db
    )

    return {"detail": "Unfollowed successfully."}

@router.get("/users/{username}/followers", response_model=list[UserOut])
async def get_followers(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    query = (
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.followee_id == user.id)
    )
    result = await db.execute(query)
    followers = result.scalars().all()
     
    if not followers:
        response = JSONResponse(content=[])
        response.headers["X-Message"] = "No followers yet"
        
    return followers 


@router.get("/users/{username}/following", response_model=list[UserOut])
async def get_following(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    query = (
        select(User)
        .join(Follow, Follow.followee_id == User.id)
        .where(Follow.follower_id == user.id)
    )
    result = await db.execute(query)
    following = result.scalars().all()

    if not following:
        response = JSONResponse(content=[])
        response.headers["X-Message"] = "No followees yet"
        return response

    return following

@router.get("/counts/{user_id}")
async def get_follow_stats(user_id: int, db: AsyncSession = Depends(get_db)):
    follower_count = await get_follower_count(user_id, db)
    following_count = await get_following_count(user_id, db)
    return {
        "user_id": user_id,
        "follower_count": follower_count,
        "following_count": following_count
    }