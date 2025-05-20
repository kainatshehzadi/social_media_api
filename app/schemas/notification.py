from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict

class NotificationBase(BaseModel):
    type: str
    data: Optional[Dict] = None

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationOut(NotificationBase):
    id: int
    content: str
    is_read: bool
    created_at: datetime

    class Config:
       from_attributes = True
class NotificationOut(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True