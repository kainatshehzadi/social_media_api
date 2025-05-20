import os
import aiofiles
from fastapi import UploadFile, HTTPException
from app.core.config import POST_MEDIA_DIR

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "mp4"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

async def save_post_media(file: UploadFile, post_id: int):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file extension")

    # Read the entire file to check size and save asynchronously
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    # Ensure the directory exists
    os.makedirs(POST_MEDIA_DIR, exist_ok=True)

    path = os.path.join(POST_MEDIA_DIR, f"{post_id}.{ext}")

    async with aiofiles.open(path, 'wb') as out_file:
        await out_file.write(content)

    await file.close()
