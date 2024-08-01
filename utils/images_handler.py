from typing import List, Tuple
from fastapi import UploadFile
from config.files import UPLOAD_DIRECTORY_SERVICES, UPLOAD_DIRECTORY_PROFILES
from PIL import Image
import os
import uuid
import aiofiles

MAX_IMAGE_SIZE_MB = 5
UPLOAD_DIRECTORY = "path/to/upload/directory"  # Define your upload directory

def validate_images(files: List[UploadFile]) -> Tuple[List[UploadFile], List[str]]:
    error_messages = []
    valid_files = []

    for file in files:
        if file.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
            error_messages.append(f"File {file.filename} exceeds {MAX_IMAGE_SIZE_MB}MB limit")
            continue

        try:
            image = Image.open(file.file)
            image.verify()
            file.file.seek(0)
            valid_files.append(file)
        except (IOError, Image.UnidentifiedImageError):
            error_messages.append(f"File {file.filename} is not a valid image")
            continue

    return valid_files, error_messages


async def save_images(service_id: int, files: List[UploadFile], directory: str) -> List[str]:
    uploaded_files = []

    for file in files:
        sanitized_filename = file.filename.replace(" ", "_")
        unique_filename = f"{service_id}_{uuid.uuid4()}_{sanitized_filename}"
        file_location = os.path.join(UPLOAD_DIRECTORY_SERVICES if directory == "services" else UPLOAD_DIRECTORY_PROFILES, unique_filename)

        async with aiofiles.open(file_location, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)

        uploaded_files.append(unique_filename)

    return uploaded_files