import logging
import traceback
from sqlalchemy.orm import selectinload
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Response, status, Path
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app import models
from app.crud.post import (
    create_post,
    get_post_by_id,
    update_post,
    delete_post,
    get_all_posts,
    get_feed_posts,
)
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.db.database import get_db
from app.models.user import User
from app.crud.user import get_current_user
from app.media.post import save_post_media

router = APIRouter(prefix="/posts", tags=["Posts"])
logger = logging.getLogger(__name__)

logger = logging.getLogger("uvicorn.error")

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_new_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        logger.info("Received post data: %s", post_data)
        logger.info("Current user: %s", current_user.id)

        new_post = await create_post(db, post_data, current_user.id)
        
        logger.info("Post created successfully with ID: %s", new_post.id)
        return new_post

    except HTTPException as e:
        raise e  # Let known HTTPExceptions pass through
    except Exception as e:
        import traceback
        traceback_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error("Unexpected error:\n%s", traceback_str)
        raise HTTPException(status_code=500, detail="Failed to create post due to an unexpected error.")

@router.get("/{post_id}", response_model=PostResponse)
async def read_post(
    post_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = await get_post_by_id(post_id, db)
    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post_route(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = await get_post_by_id(post_id=post_id, db=db)
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized and auther id not matched by current user")

    updated_post = await update_post(post_id=post_id, post_data=post_data, db=db)
    return updated_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_route(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = await get_post_by_id(post_id, db)
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    await delete_post(db, post_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/", response_model=list[PostResponse])
async def get_all_public_posts(
    db: AsyncSession = Depends(get_db),
):
    return await get_all_posts(db)


@router.get("/feed", response_model=List[PostResponse])
async def get_feed(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        # Example query: get posts with hashtags preloaded
        result = await db.execute(
            select(Post)
            .options(selectinload(Post.hashtags))
            .order_by(Post.created_at.desc())
            .limit(20)
        )
        posts = result.scalars().all()
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching feed: {e}")

@router.post("/media/{post_id}")
async def upload_post_media(
    post_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ["image/jpeg", "image/png", "video/mp4"]:
        raise HTTPException(status_code=400, detail="Invalid media type")

    # Optionally: check if current_user owns the post_id here

    await save_post_media(file, post_id)

    return {"message": "Post media uploaded successfully"}
