from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DirectMessageCreate(BaseModel):
    content: str
    media_url: Optional[str] = None

class DirectMessageResponse(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    content: str
    media_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
