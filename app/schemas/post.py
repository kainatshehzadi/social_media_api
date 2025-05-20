from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class HashtagResponse(BaseModel):
    id: int
    tag: str

    class Config:
        from_attributes = True

class PostCreate(BaseModel):
    content: str
    media_urls: Optional[List[str]] = None
    visibility: Optional[str] = "public" 

class PostResponse(BaseModel):
    id: int
    author_id: int
    content: str
    media_urls: Optional[List[str]] = Field(default_factory=list)
    created_at: datetime
    updated_at: Optional[datetime] = None
    visibility: str
    hashtags: Optional[List[HashtagResponse]] = Field(default_factory=list)

    class Config:
        orm_mode = True
class PostUpdate(BaseModel):
    content: Optional[str]
    media_urls: Optional[List[str]]
    visibility: Optional[str]
class PostOut(BaseModel):
    id: int
    content: str
    media_urls: Optional[List[str]] = []
    visibility: str
    created_at: datetime
    hashtags: List[HashtagResponse] = []

    class Config:
        from_attributes = True