from sqlalchemy import Boolean, Column, Integer, String, DateTime,ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base  
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    post = relationship("Post", back_populates="comments")
    author = relationship("User",back_populates="comments")