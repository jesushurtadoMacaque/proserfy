import uuid
from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from config.files import UPLOAD_DIRECTORY
from custom_exceptions.users_exceptions import GenericException
from models.professional_service import Comment, ProfessionalService, Rating, ServiceImage, SubCategory
from models.user import User, Role
from schemas.profesional_service_schema import CommentCreate, CommentResponse, ProfessionalServiceCreate, ProfessionalServiceResponse, RatingCreate, RatingResponse
from config.database import SessionLocal
from typing import Annotated, List
from sqlalchemy.orm import Session
from utils.error_handler import validation_error_response
from utils.getters_handler import get_user_by_email
from utils.jwt_handler import verify_token
from passlib.context import CryptContext
from PIL import Image
import aiofiles
import os



router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    user_email = payload.get("sub")
    if user_email is None:
        raise GenericException(message="Invalid authentication credentials", code=status.HTTP_401_UNAUTHORIZED)
    return user_email

@router.post("/professional-services", tags=["professional_services"], response_model=ProfessionalServiceResponse)
async def create_professional_service(service: ProfessionalServiceCreate, db: db_dependency, current_user: str = Depends(get_current_user)):
    user = get_user_by_email(db, current_user)
    if user.role.name != "professional":
        raise GenericException(message="Not authorized to create services", code=status.HTTP_403_FORBIDDEN)
    
    subcategory = db.query(SubCategory).filter(SubCategory.id == service.subcategory_id).first()
    if not subcategory:
        raise GenericException(message="Subcategory not found", code=status.HTTP_404_NOT_FOUND)

    db_service = ProfessionalService(**service.model_dump(), professional_id=user.id)
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

@router.post("/upload-images/{service_id}")
async def upload_images(
    service_id: int, 
    db: db_dependency, 
    files: List[UploadFile] = File(...), 
    current_user: str = Depends(get_current_user)):

    professional_service = db.query(ProfessionalService).filter(ProfessionalService.id == service_id).first()
    user = get_user_by_email(db, current_user)

    if professional_service.professional_id != user.id:
        raise GenericException(message="You are not the owner of this service", code=status.HTTP_401_UNAUTHORIZED)

    existing_images_count = db.query(ServiceImage).filter(ServiceImage.service_id == service_id).count()
    if existing_images_count >= 10:
        raise GenericException(message="This service already has the maximum number of 10 images.", code=status.HTTP_400_BAD_REQUEST)
    
    if len(files) + existing_images_count > 10:
        raise GenericException(message=f"Cannot upload these images. This service can only have {10 - existing_images_count} more images.", code=status.HTTP_400_BAD_REQUEST)

    error_messages = []
    valid_files = []

    for file in files:
        if file.size > 5 * 1024 * 1024:
            error_messages.append(f"File {file.filename} exceeds 5MB limit")
            continue

        try:
            image = Image.open(file.file)
            image.verify()
            file.file.seek(0) 
            valid_files.append(file)
        except (IOError, Image.UnidentifiedImageError):
            error_messages.append(f"File {file.filename} is not a valid image")
            continue

    uploaded_files = []
    for file in valid_files:
        unique_filename = f"{service_id}_{uuid.uuid4()}_{file.filename}"
        file_location = os.path.join(UPLOAD_DIRECTORY, unique_filename)

        async with aiofiles.open(file_location, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        image_url = f"/uploaded_images/services/{unique_filename}"

        service_image = ServiceImage(url=image_url, service_id=service_id)
        db.add(service_image)
        db.commit()
        db.refresh(service_image)
        
        uploaded_files.append(unique_filename)

    response = {
        "detail": "Images uploaded successfully",
        "uploaded_files": uploaded_files,
        "errors": error_messages
    }

    return JSONResponse(content=response)
@router.get("/professional-services", tags=["professional_services"], response_model=List[ProfessionalServiceResponse])
async def get_professional_services(db: db_dependency):
    return db.query(ProfessionalService).all()

@router.delete("/delete-image/{image_id}", tags=["professional_services"])
async def delete_image(image_id: int, db: db_dependency, current_user: str = Depends(get_current_user)):
    # Obtener la imagen del servicio desde la base de datos
    service_image = db.query(ServiceImage).filter(ServiceImage.id == image_id).first()
    
    if not service_image:
        raise GenericException(message="Image not found", code=status.HTTP_404_NOT_FOUND)

    professional_service = db.query(ProfessionalService).filter(ProfessionalService.id == service_image.service_id).first()
    user = get_user_by_email(db, current_user)
    
    if professional_service.professional_id != user.id:
        raise GenericException(message="You are not the owner of this service", code=status.HTTP_401_UNAUTHORIZED)

    image_path = os.path.join(UPLOAD_DIRECTORY, os.path.basename(service_image.url))
    if os.path.exists(image_path):
        os.remove(image_path)
    
    db.delete(service_image)
    db.commit()
    
    return {"detail": "Image deleted successfully"}


@router.post("/comments", tags=["comments"], response_model=CommentResponse)
async def create_comment(comment: CommentCreate, db: db_dependency, current_user: str = Depends(get_current_user)):
    user = get_user_by_email(db, current_user)
    professional_service = db.query(ProfessionalService).filter(ProfessionalService.id == comment.professional_service_id).first()
    if not professional_service:
        raise GenericException(message="Service not found", code=status.HTTP_404_NOT_FOUND)
    
    db_comment = Comment(**comment.dict(), user_id=user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.post("/ratings", tags=["ratings"], response_model=RatingResponse)
async def create_rating(rating: RatingCreate, db: db_dependency, current_user: str = Depends(get_current_user)):
    user = get_user_by_email(db, current_user)
    professional_service = db.query(ProfessionalService).filter(ProfessionalService.id == rating.professional_service_id).first()
    if not professional_service:
        raise GenericException(message="Service not found", code=status.HTTP_404_NOT_FOUND)

    existing_rating = db.query(Rating).filter(
        Rating.user_id == user.id,
        Rating.professional_service_id == rating.professional_service_id
    ).first()

    if existing_rating:
        raise GenericException(message="You have already rated this service", code=status.HTTP_400_BAD_REQUEST)

    db_rating = Rating(**rating.dict(), user_id=user.id)
    db.add(db_rating)
    db.commit()

    # Update average rating
    ratings = db.query(Rating).filter(Rating.professional_service_id == rating.professional_service_id).all()
    average_rating = sum(r.rating for r in ratings) / len(ratings)

    professional_service.average_rating = average_rating
    db.commit()

    db.refresh(db_rating)
    return db_rating

