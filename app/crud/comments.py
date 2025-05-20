from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.comments import Comment
from typing import List, Optional
from app.models.user import User
from app.schemas.comments import CommentCreate

async def create_comment(db: AsyncSession, comment: CommentCreate, user_id: int):
    new_comment = Comment(content=comment.content, post_id=comment.post_id, author_id=user_id)
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment

async def get_player_id_by_user_id(db: AsyncSession, user_id: int) -> Optional[str]:
    user = await db.get(User, user_id)
    if user:
        return user.player_id  
    return None


async def get_comments_by_post(db: AsyncSession, post_id: int) -> List[Comment]:
    result = await db.execute(
        select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at.desc())
    )
    return result.scalars().all()

async def get_comment(db: AsyncSession, comment_id: int) -> Optional[Comment]:
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    return result.scalar_one_or_none()

async def update_comment(db: AsyncSession, comment_id: int, new_content: str):
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalars().first()
    if comment:
        comment.content = new_content
        await db.commit()
        await db.refresh(comment)
        return comment
    return None


async def delete_comment(db: AsyncSession, comment_id: int) -> bool:
    comment = await get_comment(db, comment_id)
    if comment:
        await db.delete(comment)
        await db.commit()
        return True
    return False
async def get_comment_by_id(db: AsyncSession, comment_id: int):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    return result.scalar_one_or_none()
