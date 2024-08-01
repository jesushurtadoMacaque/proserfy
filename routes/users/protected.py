import os
from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from config.files import UPLOAD_DIRECTORY_PROFILES
from custom_exceptions.users_exceptions import GenericException
from custom_exceptions.users_exceptions import GenericException
from models.profile_images import ProfileImage
from models.users import User
from schemas.profesional_service_schema import ImageUpdatedResponse
from schemas.user_schema import (
    ChangePasswordRequest,
    CompleteProfile,
    UserResponse,
    ChangeRoleRequest,
    SuspendUserRequest,
    UserUpdate,
)
from config.database import db_dependency
from utils.error_handler import validation_error_response
from utils.getters_handler import get_current_user, get_role_by_id, get_user_by_email
from utils.images_handler import save_images, validate_images
from utils.password_handler import verify_password, hash_password

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


@router.put(
    "/users",
    tags=["users"],
    response_model=UserResponse,
    responses=validation_error_response,
)
async def update_user(
    user_update: UserUpdate,
    db: db_dependency,
    current_user: User = Depends(get_current_active_user),
):

    if user_update.first_name:
        current_user.first_name = user_update.first_name
    if user_update.last_name:
        current_user.last_name = user_update.last_name
    if user_update.receive_promotions is not None:
        current_user.receive_promotions = user_update.receive_promotions
    if user_update.latitude:
        current_user.latitude = user_update.latitude
    if user_update.longitude:
        current_user.longitude = user_update.longitude

    db.commit()
    db.refresh(current_user)
    return current_user


@router.put(
    "/users/change-role",
    tags=["users"],
    response_model=UserResponse,
    responses=validation_error_response,
)
async def change_user_role(
    db: db_dependency,
    request: ChangeRoleRequest,
    current_user: User = Depends(get_current_active_user),
):
    new_role = get_role_by_id(db, request.role_id)
    if new_role:
        current_user.role = new_role
        db.commit()
        db.refresh(current_user)
        return current_user
    else:
        raise GenericException(
            message="Role not exists", code=status.HTTP_404_NOT_FOUND
        )


@router.put(
    "/users/suspend",
    tags=["users"],
    response_model=UserResponse,
    responses=validation_error_response,
)
async def suspend_user(
    db: db_dependency,
    request: SuspendUserRequest,
    current_user: User = Depends(get_current_active_user),
):

    if current_user:
        current_user.is_active = request.is_active
        db.commit()
        return current_user
    else:
        raise GenericException(
            message="User not exists", code=status.HTTP_404_NOT_FOUND
        )


@router.put(
    "/user/change-password",
    tags=["users"],
    response_model=UserResponse,
    responses=validation_error_response,
)
async def change_password(
    change_password_request: ChangePasswordRequest,
    db: db_dependency,
    current_user: User = Depends(get_current_active_user),
):

    if not current_user.password:
        raise GenericException(
            message="You are registered by social", code=status.HTTP_401_UNAUTHORIZED
        )

    if not verify_password(
        change_password_request.current_password, current_user.password
    ):
        raise GenericException(
            message="Invalid password", code=status.HTTP_401_UNAUTHORIZED
        )

    if change_password_request.current_password == change_password_request.new_password:
        raise GenericException(
            message="New password must be different from the current password",
            code=status.HTTP_400_BAD_REQUEST,
        )

    current_user.password = hash_password(change_password_request.new_password)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.put(
    "/users/social/complete-profile",
    tags=["users"],
    response_model=UserResponse,
    responses=validation_error_response,
)
async def complete_profile(
    complete_profile: CompleteProfile,
    db: db_dependency,
    current_user: User = Depends(get_current_active_user),
):

    if current_user.birth_date:
        raise GenericException(
            message="You already have a birthday", code=status.HTTP_401_UNAUTHORIZED
        )

    current_user.birth_date = complete_profile.birth_date
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post(
    "/upload-profile-image",
    tags=["user_profile"],
    response_model=ImageUpdatedResponse,
)
async def upload_profile_image(
    db: db_dependency,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
):
    valid_files, error_messages = validate_images([file])
    if not valid_files:
        raise GenericException(
            message="No valid images to upload.",
            code=status.HTTP_400_BAD_REQUEST,
        )
    profile_image = db.query(ProfileImage).filter(ProfileImage.user_id == current_user.id).first()
    if profile_image:
        old_image_path = os.path.join(profile_image.url.strip("/"))
        if os.path.exists(old_image_path):
            os.remove(old_image_path)
        
        # Delete the old profile image record from the database
        db.delete(profile_image)
        db.commit()
    
   

    uploaded_files = await save_images(current_user.id, valid_files, directory="profiles")

    profile_image_url = f"/{UPLOAD_DIRECTORY_PROFILES}/{uploaded_files[0]}"
    profile_image = ProfileImage(
        url=profile_image_url,
        user_id=current_user.id
    )
    db.add(profile_image)
    db.commit()

    response = ImageUpdatedResponse(
        detail="Profile image uploaded successfully",
        uploaded_files=uploaded_files,
        errors=error_messages,
    )

    return response
