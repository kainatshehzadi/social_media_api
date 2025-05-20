from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models import Hashtag

router = APIRouter(prefix="/tags", tags=["Hashtags"])

@router.get("/{tag}")
def get_posts_by_hashtag(tag: str, db: Session = Depends(get_db)):
    hashtag = db.query(Hashtag).filter(Hashtag.tag == tag.lower()).first()
    if not hashtag:
        raise HTTPException(status_code=404, detail="Hashtag not found")
    return hashtag.posts
