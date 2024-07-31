from fastapi import APIRouter, Depends, status
from custom_exceptions.users_exceptions import GenericException
from models.professional_services import ProfessionalService
from models.ratings import Rating
from models.users import User
from routes.professional_services.protected import get_current_active_user
from schemas.profesional_service_schema import RatingCreate, RatingResponse
from config.database import db_dependency

router = APIRouter()

@router.post("/ratings", tags=["ratings"], response_model=RatingResponse)
async def create_rating(
    rating: RatingCreate,
    db: db_dependency,
    current_user: User = Depends(get_current_active_user),
):

    professional_service = (
        db.query(ProfessionalService)
        .filter(ProfessionalService.id == rating.professional_service_id)
        .first()
    )
    if not professional_service:
        raise GenericException(
            message="Service not found", code=status.HTTP_404_NOT_FOUND
        )

    existing_rating = (
        db.query(Rating)
        .filter(
            Rating.user_id == current_user.id,
            Rating.professional_service_id == rating.professional_service_id,
        )
        .first()
    )

    if existing_rating:
        raise GenericException(
            message="You have already rated this service",
            code=status.HTTP_400_BAD_REQUEST,
        )

    db_rating = Rating(**rating.model_dump(), user_id=current_user.id)
    db.add(db_rating)
    db.commit()

    ratings = (
        db.query(Rating)
        .filter(Rating.professional_service_id == rating.professional_service_id)
        .all()
    )
    average_rating = sum(r.rating for r in ratings) / len(ratings)

    professional_service.average_rating = average_rating
    db.commit()

    db.refresh(db_rating)
    return db_rating
