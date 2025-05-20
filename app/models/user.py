from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.follow import Follow
from app.models.post import Post


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    player_id = Column(String, nullable=True)
    bio = Column(String, nullable=False, default="")
    avatar_url = Column(String(300), nullable=False, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    followers = relationship("Follow",foreign_keys=[Follow.followee_id],back_populates="followee",cascade="all, delete-orphan")
    following = relationship("Follow",foreign_keys=[Follow.follower_id],back_populates="follower",cascade="all, delete-orphan")
    posts = relationship("Post", foreign_keys=[Post.user_id], back_populates="user", cascade="all, delete-orphan")
    authored_posts = relationship("Post", foreign_keys=[Post.author_id], back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

