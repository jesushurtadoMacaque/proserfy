import uuid
from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from config.files import UPLOAD_DIRECTORY_SERVICES
from custom_exceptions.users_exceptions import GenericException
from models.professional_services import ProfessionalService, WorkSchedule
from models.service_images import ServiceImage
from models.subcategories import SubCategory
from models.users import User
from schemas.profesional_service_schema import (
    ImageUpdatedResponse,
    ProfessionalServiceCreate,
    ProfessionalServiceResponse,
)
from config.database import db_dependency
from typing import List
from utils.getters_handler import get_current_user, get_user_by_email
from PIL import Image
import aiofiles
import os

from utils.images_handler import save_images, validate_images

router = APIRouter()


async def get_current_active_user(
    request: Request, db: db_dependency, current_user: str = Depends(get_current_user)
):
    user = get_user_by_email(db, current_user)
    if not user:
        raise GenericException(
            message="User not exists", code=status.HTTP_404_NOT_FOUND
        )
    if not user.is_active:
        raise GenericException(
            message="User is suspended", code=status.HTTP_403_FORBIDDEN
        )
    return user


@router.post(
    "/professional-services",
    tags=["professional_services"],
    response_model=ProfessionalServiceResponse,
)
async def create_professional_service(
    service: ProfessionalServiceCreate,
    db: db_dependency,
    current_user: User = Depends(get_current_active_user),
):

    if current_user.role.name != "professional":
        raise GenericException(
            message="Not authorized to create services", code=status.HTTP_403_FORBIDDEN
        )

    subcategory = (
        db.query(SubCategory).filter(SubCategory.id == service.subcategory_id).first()
    )
    if not subcategory:
        raise GenericException(
            message="Subcategory not found", code=status.HTTP_404_NOT_FOUND
        )

    try:
        db_service = ProfessionalService(
            name=service.name,
            description=service.description,
            range_from= service.range_from,
            range_to= service.range_to,
            city=service.city,
            latitude=service.latitude,
            longitude=service.longitude,
            subcategory_id=service.subcategory_id,
            professional_id=current_user.id
        )
        db.add(db_service)
        db.commit()
        db.refresh(db_service)

        # Crear los WorkSchedules
        for schedule in service.work_schedules:
            db_schedule = WorkSchedule(
                day_of_week=schedule.day_of_week,
                start_time=schedule.start_time,
                end_time=schedule.end_time,
                is_active=schedule.is_active,
                professional_service_id=db_service.id
            )
            db.add(db_schedule)
        
        db.commit()
    except:
        db.rollback()
        raise

    db.refresh(db_service)
    return db_service


@router.post(
    "/upload-images/{service_id}",
    tags=["professional_services"],
    response_model=ImageUpdatedResponse,
)
async def upload_images(
    service_id: int,
    db: db_dependency,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
):

    professional_service = (
        db.query(ProfessionalService)
        .filter(ProfessionalService.id == service_id)
        .first()
    )

    if (
        not professional_service
        or professional_service.professional_id != current_user.id
    ):
        raise GenericException(
            message="Error trying to update", code=status.HTTP_401_UNAUTHORIZED
        )

    existing_images_count = (
        db.query(ServiceImage).filter(ServiceImage.service_id == service_id).count()
    )
    if existing_images_count >= 10:
        raise GenericException(
            message="This service already has the maximum number of 10 images.",
            code=status.HTTP_400_BAD_REQUEST,
        )

    if len(files) + existing_images_count > 10:
        raise GenericException(
            message=f"Cannot upload these images. This service can only have {10 - existing_images_count} more images.",
            code=status.HTTP_400_BAD_REQUEST,
        )


    valid_files, error_messages = validate_images(files)
    uploaded_files = await save_images(service_id, valid_files, directory="services")

    for file_name in uploaded_files:
        image_url = f"/uploaded_images/services/{file_name}"
        service_image = ServiceImage(url=image_url, service_id=service_id)
        db.add(service_image)
        db.commit()
        db.refresh(service_image)

    response = ImageUpdatedResponse(
        detail="Images uploaded successfully",
        uploaded_files=uploaded_files,
        errors=error_messages,
    )

    return response


@router.delete("/delete-image/{image_id}", tags=["professional_services"])
async def delete_image(
    image_id: int,
    db: db_dependency,
    current_user: User = Depends(get_current_active_user),
):

    service_image = db.query(ServiceImage).filter(ServiceImage.id == image_id).first()

    if not service_image:
        raise GenericException(
            message="Image not found", code=status.HTTP_404_NOT_FOUND
        )

    professional_service = (
        db.query(ProfessionalService)
        .filter(ProfessionalService.id == service_image.service_id)
        .first()
    )

    if professional_service.professional_id != current_user.id:
        raise GenericException(
            message="You are not the owner of this service",
            code=status.HTTP_401_UNAUTHORIZED,
        )

    image_path = os.path.join(UPLOAD_DIRECTORY_SERVICES, os.path.basename(service_image.url))
    if os.path.exists(image_path):
        os.remove(image_path)

    db.delete(service_image)
    db.commit()

    return {"detail": "Image deleted successfully"}
