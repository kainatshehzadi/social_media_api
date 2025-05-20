from pydantic import BaseModel
from datetime import datetime

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    post_id: int
    author_id: int  # or get from current user session (preferable)

class CommentUpdate(CommentBase):
    content:str

class CommentResponse(CommentBase):
    id: int
    post_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
