from pydantic import BaseModel, EmailStr, Field, HttpUrl, ValidationError, field_validator
from typing import Optional
from datetime import datetime

# Base class for user validation
class UserBase(BaseModel):
    username: str
    email: EmailStr
    bio: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    is_active: bool

    class Config:
        from_attribute = True 

# Schema for creating a new user, includes password
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=8)  # Password validation with minimum length
    player_id: Optional[str] = None
    bio: Optional[str] = None  # Optional field with default None
    avatar_url: Optional[str] = None 

# Schema for returning user details in response
class UserResponse(BaseModel):
    id: int
    username: str
    bio: str | None
    avatar_url: HttpUrl | None
    

    class Config:
        from_attributes = True

# Schema for login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str
#Schema for adding and updating public user/profile
class UserPublic(BaseModel):
    id : int
    username: str
    email: EmailStr
    bio: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None

    class Config:
        from_attributes = True  


class UpdateUser(BaseModel):
    bio: str = Field(..., max_length=300)  # Example length limit for bio
    avatar_url: str  # Assuming avatar_url is a valid URL

    class Config:
        from_attribute = True 
@field_validator("avatar_url")
@classmethod
def validate_avatar_url(cls, v):
        if v is not None:
            try:
                HttpUrl.validate(v)
            except ValidationError:
                raise ValueError("Invalid avatar URL")
        return v 
class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

#its the schemas of follower,followee user
class UserOut(BaseModel):
    id: int
    username: str
    email: str
    bio: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    created_at: datetime

    followers_count: Optional[int] = 0
    following_count: Optional[int] = 0


    class Config:
        from_attributes = True

