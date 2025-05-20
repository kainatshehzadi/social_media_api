from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.crud.post import get_post_by_id
from app.models.like import Like
from app.schemas.like import LikeBase, LikeResponse
from app.db.database import get_db
from app.crud.like import like_post, unlike_post, get_likes_for_post
from app.models.user import User
from app.crud.user import get_current_user

router = APIRouter(prefix="/likes", tags=["Likes"])

@router.post("/posts/{post_id}/like")
async def like_post(post_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    post = get_post_by_id(db, post_id)  # Get the post being liked
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Save like logic here
    like =Like(user_id=current_user.id, post_id=post_id)
    db.add(like)
    db.commit()
    
    #  Send OneSignal notification to post owner
    if post.user_id != current_user.id:  # Don't notify self
        recipient = db.query(User).filter(User.id == post.user_id).first()
        if recipient and recipient.player_id:
            from app.utils.notification import send_onesignal_notification
            await send_onesignal_notification(
                player_id=recipient.player_id,
                heading="New Like",
                content=f"{current_user.username} liked your post!"
            )

    return {"message": "Post liked"}



@router.delete("/", status_code=204)
async def unlike(
    data: LikeBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = await unlike_post(db, current_user.id, data.post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Like not found")


@router.get("/post/{post_id}", response_model=List[LikeResponse])
async def get_likes(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_likes_for_post(db, post_id)
