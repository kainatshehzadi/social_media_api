from sqlalchemy.orm import Session
from app import models
from app.schemas.notification import NotificationCreate

def create_notification(db: Session, notification:NotificationCreate) -> models.Notification:
    db_notification = models.Notification(
        recipient_id=notification.user_id,
        type=notification.type,
        data=notification.data or {},
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notifications_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    return db.query(models.Notification)\
             .filter(models.Notification.user_id == user_id)\
             .order_by(models.Notification.created_at.desc())\
             .offset(skip).limit(limit).all()

def mark_notification_as_read(db: Session, notification_id: int):
    notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not notification:
        return None
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification
