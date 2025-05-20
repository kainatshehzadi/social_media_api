import os
from fastapi import UploadFile

async def save_avatar(file: UploadFile, user_id: int) -> str:
    # Define the directory path where avatars will be saved
    directory = os.path.join("app", "media", "avatars")

    # Create the directory if it does not exist
    os.makedirs(directory, exist_ok=True)

    filename = f"{user_id}.jpg"
    path = os.path.join(directory, filename)

    # Save the uploaded file to disk
    with open(path, "wb") as buffer:
        buffer.write(await file.read())

    # Return the relative URL or path to be saved in DB or sent as response
    return f"/media/avatars/{filename}"
