import os
import httpx
import logging

logger = logging.getLogger(__name__)

ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID", "YOUR_ONESIGNAL_APP_ID")
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY", "YOUR_ONESIGNAL_REST_API_KEY")

async def send_onesignal_notification(player_id: str, heading: str, content: str):
    url = "https://onesignal.com/api/v1/notifications"

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}"
    }

    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "include_player_ids": [player_id],
        "headings": {"en": heading},
        "contents": {"en": content}
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            logger.info("Push notification sent successfully")
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error while sending push notification: {exc.response.status_code} - {exc.response.text}")
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
