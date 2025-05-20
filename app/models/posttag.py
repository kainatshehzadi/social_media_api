from sqlalchemy import Table, Column, ForeignKey
from app.db.database import Base 

post_hashtags = Table(
    'post_hashtags',
    Base.metadata,
    Column('post_id', ForeignKey('posts.id'), primary_key=True),
    Column('hashtag_id', ForeignKey('hashtags.id'), primary_key=True),
)
