# app/routers/media.py
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends
from media.files import validate_file, save_file
from app.crud.user import get_current_user
from typing import Literal

router = APIRouter(prefix="/upload", tags=["Media"])

@router.post("/{folder}")
async def upload_media(
    folder: Literal["posts", "avatars"],
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = Depends(),
    current_user=Depends(get_current_user)
):
    validate_file(file)
    
    def process():
        save_file(file, folder)

    background_tasks.add_task(process)

    return {"message": "Upload received and will be saved shortly."}
