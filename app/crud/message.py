from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import DirectMessage
from app.models.user import User
from app.schemas.message import DirectMessageCreate
from app.utils.pusher import pusher_client
from fastapi import HTTPException, status

async def send_direct_message(
    db: AsyncSession,
    sender_id: int,
    recipient_username: str,
    message_data: DirectMessageCreate
):
    result = await db.execute(select(User).filter(User.username == recipient_username))
    recipient = result.scalars().first()

    if not recipient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")

    message = DirectMessage(
        sender_id=sender_id,
        recipient_id=recipient.id,
        content=message_data.content,
        media_url=message_data.media_url,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    try:
        pusher_client.trigger(
            f"user_{recipient.id}",
            "new_message",
            {
                "sender_id": sender_id,
                "content": message_data.content,
                "media_url": message_data.media_url,
            }
        )
    except Exception as e:
        # Log or handle pusher error here if needed
        pass

    return message
