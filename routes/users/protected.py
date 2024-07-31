from fastapi import APIRouter, Depends, Request, status
from custom_exceptions.users_exceptions import GenericException
from models.users import User
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
