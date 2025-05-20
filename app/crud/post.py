import random
import string
import traceback
from sqlalchemy import or_, select,func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import logging
from sqlalchemy.orm import selectinload
from app.models.hashtag import Hashtag
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate
from app.utils.hashtag import extract_hashtags
from app.models.posttag import post_hashtags

async def create_post(db: AsyncSession, post_data: PostCreate, user_id: int) -> Post:
    try:
        new_post = Post(
            content=post_data.content,
            media_urls=post_data.media_urls,
            visibility=post_data.visibility,
            author_id=user_id
        )
        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)
        return new_post

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Database error occurred while creating post.")
    
async def get_post_by_id(db: AsyncSession, post_id: int) -> Post:
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
    return post


def generate_random_media_url(length: int = 10) -> str:
    letters_and_digits = string.ascii_letters + string.digits
    random_str = ''.join(random.choice(letters_and_digits) for _ in range(length))
    return f"https://example.com/media/{random_str}"


async def update_post(post_id: int, post_data: PostUpdate, db: AsyncSession) -> Post | None:
    post = await get_post_by_id(post_id, db)
    for key, value in post_data.dict(exclude_unset=True).items():
        setattr(post, key, value)
    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(db: AsyncSession, post_id: int) -> bool:
    post = await db.get(Post, post_id)
    if post:
        await db.delete(post)
        await db.commit()
        return True
    return False


async def get_all_posts(db: AsyncSession) -> list[Post]:
    result = await db.execute(select(Post))
    return result.scalars().all()


async def get_feed_posts(db: AsyncSession, user_id: int) -> list[Post]:
    result = await db.execute(select(Post))
    return result.scalars().all()


async def search_posts_by_hashtag_or_content(db: AsyncSession, keyword: str):
    pattern = f"%{keyword.lower()}%"
    stmt = (
        select(Post)
        .outerjoin(Post.hashtags)
        .filter(
            or_(
                Hashtag.tag.ilike(pattern),
                Post.content.ilike(pattern),
            )
        )
        .options(selectinload(Post.hashtags))
        .distinct()
    )
    result = await db.execute(stmt)
    posts = result.scalars().all()
    return posts
