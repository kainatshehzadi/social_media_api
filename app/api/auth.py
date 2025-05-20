from datetime import time
from os import stat
from fastapi import status
import time
from fastapi import APIRouter, Depends, HTTPException ,status as stat
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.crud.post import generate_random_media_url
from app.db.database import get_db # type: ignore
from app import schemas, crud
from app.core.utils import create_access_token, verify_password # type: ignore
from app.schemas.user import  OTPVerifyRequest, TokenResponse, UserCreate, UserLogin, UserResponse # type: ignore
from app.crud.user import authenticate_user, create_user, get_user_email # type: ignore
from app.utils.email import send_email_verification # type: ignore
from app.utils.hashing import get_password_hash
from app.utils.otp import generate_otp # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.email import send_email_verification 
from app.schemas.user import UserCreate

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
otp_storage = {}
# Register endpoint where OTP is generated and stored
@router.post("/register", status_code=status.HTTP_202_ACCEPTED)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    email = user.email.strip().lower()

    # Check if email already exists
    existing_user = await get_user_email(db, email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate OTP and store temporarily with timestamp and full user data
    generated_otp = generate_otp()
    otp_storage[email] = {
        "otp": generated_otp,
        "timestamp": time.time(),
        "user_data": user.dict(),  # This includes password
    }

    # Send OTP email (should return True/False)
    email_sent = send_email_verification(email, generated_otp)
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send OTP email")

    return {"message": "OTP sent to your email for verification"}


@router.post("/verify-otp")
async def verify_otp(otp_request: OTPVerifyRequest, db: AsyncSession = Depends(get_db)):
    email = otp_request.email.strip().lower()
    stored_data = otp_storage.get(email)

    if not stored_data:
        raise HTTPException(status_code=404, detail="OTP not found or expired")

    if time.time() - stored_data["timestamp"] > 600:
        del otp_storage[email]
        raise HTTPException(status_code=400, detail="OTP expired")

    if otp_request.otp != stored_data["otp"]:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user_data = stored_data["user_data"]

    avatar_url = str(user_data.get("avatar_url")) if user_data.get("avatar_url") else generate_random_media_url()


    try:
        
        user_create = UserCreate(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],  
            player_id=user_data.get("player_id"),
            bio=user_data.get("bio", ""),
            avatar_url=str(avatar_url),
        )

        new_user = await create_user(db, user_create)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User creation failed: {e}")

    del otp_storage[email]

    return {
        "message": "User registered successfully",
        "user": new_user.username,
    }

# Login user

@router.post("/login", response_model=TokenResponse)
async def login_user(request: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, request.email, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token_data = {"user_id": user.id}
    access_token = create_access_token(data=token_data)

    return {"access_token": access_token, "token_type": "bearer"}
