from fastapi import APIRouter, Depends, status
from custom_exceptions.users_exceptions import GenericException
from models.professional_services import ProfessionalService
from models.comments import Comment
from models.users import User
from routes.professional_services.protected import get_current_active_user
from schemas.profesional_service_schema import CommentCreate, CommentResponse
from config.database import db_dependency
from utils.getters_handler import get_current_user, get_user_by_email

router = APIRouter()


@router.post("/comments", tags=["comments"], response_model=CommentResponse)
async def create_comment(
    comment: CommentCreate,
    db: db_dependency,
    current_user: User = Depends(get_current_active_user),
):

    professional_service = (
        db.query(ProfessionalService)
        .filter(ProfessionalService.id == comment.professional_service_id)
        .first()
    )
    if not professional_service:
        raise GenericException(
            message="Service not found", code=status.HTTP_404_NOT_FOUND
        )

    db_comment = Comment(**comment.model_dump(), user_id=current_user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment
