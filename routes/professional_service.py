import uuid
from fastapi import APIRouter, Depends, File, Query, Request, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from config.files import UPLOAD_DIRECTORY
from custom_exceptions.users_exceptions import GenericException
from models.professional_service import Comment, ProfessionalService, Rating, ServiceImage, SubCategory
from schemas.paginated_schema import PaginatedResponse
from schemas.profesional_service_schema import CommentCreate, CommentResponse, ImageUpdatedResponse, ProfessionalServiceCreate, ProfessionalServiceResponse, RatingCreate, RatingResponse
from config.database import SessionLocal
from typing import Annotated, List
from sqlalchemy.orm import Session
from utils.generate_url import build_pagination_urls
from utils.getters_handler import get_current_user, get_user_by_email
from PIL import Image
import aiofiles
import os

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/professional-services", tags=["professional_services"], response_model=ProfessionalServiceResponse)
async def create_professional_service(service: ProfessionalServiceCreate, db: db_dependency, current_user: str = Depends(get_current_user)):
    user = get_user_by_email(db, current_user)
    if not user: 
        raise GenericException(message="User not found", code=status.HTTP_404_NOT_FOUND)
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

@router.post("/upload-images/{service_id}", tags=["professional_services"], response_model=ImageUpdatedResponse)
async def upload_images(
    service_id: int, 
    db: db_dependency, 
    files: List[UploadFile] = File(...), 
    current_user: str = Depends(get_current_user)):

    professional_service = db.query(ProfessionalService).filter(ProfessionalService.id == service_id).first()
    user = get_user_by_email(db, current_user)

    if not professional_service or professional_service.professional_id != user.id:
        raise GenericException(message="Error trying to update", code=status.HTTP_401_UNAUTHORIZED)

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

    response = ImageUpdatedResponse(
        detail= "Images uploaded successfully",
        uploaded_files= uploaded_files,
        errors = error_messages
    )

    return JSONResponse(content=response)

@router.get("/professional-services", tags=["professional_services"], response_model=PaginatedResponse)
async def get_professional_services(
    db: db_dependency, 
    request: Request,
    limit: int = Query(15), 
    offset: int = Query(0), 
):
    query = db.query(ProfessionalService)
    total = query.count()
    services = query.limit(limit).offset(offset).all()
    
    total_pages = (total + limit - 1) // limit
    
    current_page_url, next_page_url, prev_page_url = build_pagination_urls(request, offset, limit, total)
    
    return PaginatedResponse(
        total_items=total,
        total_pages=total_pages,
        current_page=current_page_url,
        next_page=next_page_url,
        prev_page=prev_page_url,
        items=services
    )
    #return db.query(ProfessionalService).limit(limit).offset(offset).all()


@router.get("/professional-services/filter", name="Get services by location range" ,tags=["professional_services"], response_model=PaginatedResponse)
def get_services(
    db: db_dependency,
    request: Request,
    limit: int = Query(15), 
    offset: int = Query(0),
    lat: float = Query(...), 
    lon: float = Query(...), 
    range_km: float = Query(...), 
    ):

    query = db.query(ProfessionalService).filter(
        text("ST_Distance_Sphere(point(longitude, latitude), point(:lon, :lat)) <= :range_km * 1000")
    ).params(
        lon=lon, lat=lat, range_km=range_km
    )

    total = query.count()

    services = query.limit(limit).offset(offset).all()
    total_pages = (total + limit - 1) // limit
    
    current_page_url, next_page_url, prev_page_url = build_pagination_urls(request, offset, limit, total)
    

    return PaginatedResponse(
        total_items=total,
        total_pages=total_pages,
        current_page=current_page_url,
        next_page=next_page_url,
        prev_page=prev_page_url,
        items=services
    )


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
    
    db_comment = Comment(**comment.model_dump(), user_id=user.id)
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

    db_rating = Rating(**rating.model_dump(), user_id=user.id)
    db.add(db_rating)
    db.commit()

    # Update average rating
    ratings = db.query(Rating).filter(Rating.professional_service_id == rating.professional_service_id).all()
    average_rating = sum(r.rating for r in ratings) / len(ratings)

    professional_service.average_rating = average_rating
    db.commit()

    db.refresh(db_rating)
    return db_rating

    
