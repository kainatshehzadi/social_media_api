from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.like import Like
from typing import List
from app import models, schemas, crud 
from fastapi import HTTPException
from app.utils.notification import send_onesignal_notification

async def like_post(db: AsyncSession, user_id: int, post_id: int):
    result = await db.execute(
        select(models.Like).where(models.Like.user_id == user_id, models.Like.post_id == post_id)
    )
    existing_like = result.scalar_one_or_none()

    if existing_like:
        raise HTTPException(status_code=400, detail="Post already liked")

    post_result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id != user_id:
        user_result = await db.execute(select(models.User).where(models.User.id == user_id))
        liker = user_result.scalar_one_or_none()

        author_result = await db.execute(select(models.User).where(models.User.id == post.author_id))
        author = author_result.scalar_one_or_none()

        # Ensure author has a OneSignal player ID
        if author and author.onesignal_player_id:
            await send_onesignal_notification(
                to_player_id=author.onesignal_player_id,
                liker_username=liker.username,
                post_id=post_id
            )

    new_like = models.Like(user_id=user_id, post_id=post_id)
    db.add(new_like)
    await db.commit()
    await db.refresh(new_like)
    return new_like




async def unlike_post(db: AsyncSession, user_id: int, post_id: int):
    result = await db.execute(select(Like).where(Like.user_id == user_id, Like.post_id == post_id))
    like = result.scalar_one_or_none()

    if like:
        await db.delete(like)
        await db.commit()
        return True
    return False


async def get_likes_for_post(db: AsyncSession, post_id: int) -> List[Like]:
    result = await db.execute(select(Like).where(Like.post_id == post_id))
    return result.scalars().all()
