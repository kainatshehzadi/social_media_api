from pydantic import BaseModel
from datetime import datetime

class LikeBase(BaseModel):
    post_id: int

class LikeCreate(LikeBase):
    pass

class LikeResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
