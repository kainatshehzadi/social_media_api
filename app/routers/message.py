from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.message import DirectMessageCreate, DirectMessageResponse
from app.db.database import get_db
from app.crud.user import get_current_user
from app.crud.message import send_direct_message

router = APIRouter(prefix="/dm", tags=["Direct Messages"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/{username}", response_model=DirectMessageResponse)
async def send_dm(
    message: DirectMessageCreate,
    username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await send_direct_message(db, sender_id=current_user.id, recipient_username=username, message_data=message)
    return result
