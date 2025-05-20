from asyncio import create_task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, func
from app.models.user import User
from app.models.follow import Follow
from fastapi import HTTPException, status
import logging
from app.utils.notification import  send_onesignal_notification

logger = logging.getLogger(__name__)


async def perform_follow_user(follower_id: int, followee_id: int, db: AsyncSession):
    if follower_id == followee_id:
        logger.warning(f"User {follower_id} tried to follow themselves.")
        raise HTTPException(status_code=400, detail="You cannot follow yourself.")

    query = select(Follow).where(
        and_(Follow.follower_id == follower_id, Follow.followee_id == followee_id)
    )
    result = await db.execute(query)
    existing_follow = result.scalar_one_or_none()

    if existing_follow:
        logger.info(f"User {follower_id} already follows user {followee_id}.")
        raise HTTPException(status_code=409, detail="You are already following this user.")

    follow = Follow(follower_id=follower_id, followee_id=followee_id)
    db.add(follow)

    try:
        await db.commit()
        await db.refresh(follow)

        # Fetch followee's player_id (device ID from OneSignal)
        followee = await db.get(User, followee_id)
        if followee and followee.player_id:
            heading = "New Follower!"
            content = f"You have a new follower "
            send_onesignal_notification(followee.player_id, heading, content)

        logger.info(f"User {follower_id} successfully followed user {followee_id}.")
        return follow
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while following: {e}")
        raise HTTPException(status_code=500, detail="Failed to follow user.")

async def perform_unfollow_user(follower_id: int, followee_id: int, db: AsyncSession):
    query = select(Follow).where(
        and_(Follow.follower_id == follower_id, Follow.followee_id == followee_id)
    )
    result = await db.execute(query)
    follow = result.scalar_one_or_none()

    if not follow:
        logger.warning(f"User {follower_id} tried to unfollow user {followee_id}, but no follow relationship exists.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow relationship not found."
        )

    try:
        await db.delete(follow)
        await db.commit()
        logger.info(f"User {follower_id} unfollowed user {followee_id} successfully.")
        return {"detail": "Unfollowed successfully."}
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while user {follower_id} tried to unfollow user {followee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unfollow user."
        )
async def get_follower_count(user_id: int, db: AsyncSession) -> int:
    result = await db.execute(
        select(func.count()).select_from(Follow).where(Follow.followee_id == user_id)
    )
    return result.scalar()

async def get_following_count(user_id: int, db: AsyncSession) -> int:
    result = await db.execute(
        select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)
    )
    return result.scalar()