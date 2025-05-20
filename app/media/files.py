# media/files.py
import os
import shutil
from fastapi import UploadFile, HTTPException
from uuid import uuid4

ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]
MAX_FILE_SIZE_MB = 5

def validate_file(file: UploadFile):
    extension = file.filename.split(".")[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed")

    file.file.seek(0, os.SEEK_END)
    size = file.file.tell() / (1024 * 1024)
    file.file.seek(0)
    if size > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB")

def save_file(file: UploadFile, folder: str) -> str:
    extension = file.filename.split(".")[-1]
    filename = f"{uuid4().hex}.{extension}"
    folder_path = os.path.join("media", folder)
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"/media/{folder}/{filename}"
