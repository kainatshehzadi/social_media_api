from fastapi import APIRouter, Body, Depends, HTTPException, logger, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.crud.post import get_post_by_id
from app.models.comments import Comment
from app.schemas.comments import CommentCreate, CommentResponse, CommentUpdate
from app.crud.comments import create_comment, get_comments_by_post, update_comment, delete_comment, get_comment_by_id
from app.db.database import get_db
from app.models.user import User
from app.models.post import Post
from app.crud.user import get_current_user
from app.utils.notification import send_onesignal_notification 
from sqlalchemy.future import select

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/")
async def add_comment(
    comment_in: CommentCreate = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get the post by ID
    post = await get_post_by_id(db, comment_in.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Create and save the comment
    comment = Comment(
        post_id=comment_in.post_id,
        author_id=current_user.id,
        content=comment_in.content
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    # Notify the post owner (if not the current user)
    if post.user_id != current_user.id:
        recipient = await db.get(User, post.user_id)
        if recipient and recipient.player_id:
            from app.utils.notification import send_onesignal_notification
            await send_onesignal_notification(
                player_id=recipient.player_id,
                heading="New Comment",
                content=f"{current_user.username} commented on your post"
            )

    return {"message": "Comment added successfully"}
@router.get("/post/{post_id}", response_model=List[CommentResponse])
async def read_comments(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_comments_by_post(db, post_id)


@router.put("/{comment_id}", response_model=CommentResponse)
async def put_comment(
    comment_id: int,
    comment: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_comment = await get_comment_by_id(db, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")

    return await update_comment(db, comment_id, comment.content)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_endpoint(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_comment = await get_comment_by_id(db, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.author_id != current_user.id:  
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    await delete_comment(db, comment_id)
