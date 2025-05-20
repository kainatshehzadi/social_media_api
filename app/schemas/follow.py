from pydantic import BaseModel
from datetime import datetime

class FollowCreate(BaseModel):
    follower_id: int
    followee_id: int

class FollowResponse(BaseModel):
    id: int
    follower_id: int
    followee_id: int
    created_at: datetime

    class Config:
        from_attributes = True
class MessageResponse(BaseModel):
    detail: str