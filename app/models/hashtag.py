from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.posttag import post_hashtags 

class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    tag = Column(String, unique=True, index=True, nullable=False)

    posts = relationship("Post", secondary=post_hashtags, back_populates="hashtags")
