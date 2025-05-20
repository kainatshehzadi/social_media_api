from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models import Post
from app.db.database import get_db, AsyncSession
from app.schemas.post import PostOut
from app.crud.post import search_posts_by_hashtag_fuzzy
router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/posts/search", response_model=List[PostOut])
async def fuzzy_search_posts_by_hashtag(
    keyword: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db)
):
    posts = await search_posts_by_hashtag_fuzzy(db, keyword)
    return posts
