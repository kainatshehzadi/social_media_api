from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.models.post import Post
from app.models.like import Like
from app.models.user import User
from app.models.follow import Follow
from app.schemas.post import PostResponse
from app.crud.user import get_current_user

router = APIRouter(prefix="/feed", tags=["Feed & Explore"])


@router.get("/", response_model=List[PostResponse])
async def get_feed(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=50, description="Number of posts to return (max 50)"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
):
    """
    Get feed from users the current user follows. Supports pagination.
    """
    try:
        # Get IDs of users the current user is following
        result = await db.execute(
            select(Follow.followee_id).where(Follow.follower_id == current_user.id)
        )
        followee_ids = [row[0] for row in result.fetchall()]

        if not followee_ids:
            raise HTTPException(status_code=404, detail="You are not following anyone yet.")

        # Fetch posts from followed users
        result = await db.execute(
            select(Post)
            .where(Post.author_id.in_(followee_ids))
            .order_by(Post.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        posts = result.scalars().all()

        if not posts:
            raise HTTPException(status_code=404, detail="No posts available from followed users.")

        return posts

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch feed")


@router.get("/explore", response_model=List[PostResponse])
async def get_trending_posts(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=50, description="Number of posts to return (max 50)"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
):
    """
    Get trending posts sorted by number of likes. Supports pagination.
    """
    try:
        # Select posts with like counts, order by popularity and recency
        stmt = (
            select(Post, func.count(Like.id).label("like_count"))
            .join(Like, Post.id == Like.post_id, isouter=True)
            .group_by(Post.id)
            .order_by(desc("like_count"), desc(Post.created_at))
            .offset(offset)
            .limit(limit)
        )

        result = await db.execute(stmt)
        posts_with_likes = result.all()

        if not posts_with_likes:
            raise HTTPException(status_code=404, detail="No trending posts available.")

        # Return only the Post objects
        posts = [row[0] for row in posts_with_likes]
        return posts

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch trending posts")
