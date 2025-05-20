from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    followee_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # ondelete ensures proper cleanup
    created_at = Column(DateTime(timezone=True), default=func.now())

    __table_args__ = (UniqueConstraint("follower_id", "followee_id", name="unique_follow"),)

    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followee = relationship("User", foreign_keys=[followee_id], back_populates="followers")# This refers to the User model's "followers"
