from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from app import schemas, models, crud
from app.db.database import get_db
from app.crud.user import get_current_user  # your auth dependency
from app.models.user import User
from app.schemas.notification import NotificationOut
router = APIRouter()

@router.get("/notifications/", response_model=List[NotificationOut])
def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notifications = crud.get_notifications_for_user(db, current_user.id, skip=skip, limit=limit)
    return notifications

@router.put("/notifications/{notification_id}/read", response_model=NotificationOut)
def mark_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = crud.mark_notification_as_read(db, notification_id)
    if not notification or notification.recipient_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification
