from datetime import datetime, timezone
from sqlalchemy import ARRAY, TIMESTAMP, Column, Integer, String, Text, ForeignKey
from sqlalchemy import Enum as SQLAlchemyEnum

from sqlalchemy.orm import relationship
from app.api.enum import PostVisibilityEnum
from app.db.database import Base
from app.models.posttag import post_hashtags
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    media_urls = Column(ARRAY(String),nullable=True)
    visibility = Column(SQLAlchemyEnum(PostVisibilityEnum),default=PostVisibilityEnum.public)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))


    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete")
    hashtags = relationship("Hashtag",secondary=post_hashtags,back_populates="posts",lazy="selectin")
    author = relationship("User", foreign_keys=[author_id], back_populates="authored_posts")
    user = relationship("User", foreign_keys=[user_id], back_populates="posts")
