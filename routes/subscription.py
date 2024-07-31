from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, status
from config.database import db_dependency
from custom_exceptions.users_exceptions import GenericException
from models import subscriptions
from models.users import User
from routes.professional_services.protected import get_current_active_user
from schemas import subscription_schema
from schemas.user_schema import UserResponse

router = APIRouter()


@router.get(
    "/subscriptions",
    tags=["subscription"],
    response_model=List[subscription_schema.SubscriptionTypeBase],
)
def get_all_subscriptions(db: db_dependency):
    return db.query(subscriptions.SubscriptionType).all()


@router.post("/subscription", tags=["subscription"], response_model=UserResponse)
def adding_user_sub(
    request: subscription_schema.SubscriptionCreate,
    db: db_dependency,
    current_user: User = Depends(get_current_active_user),
):

    sub_type = (
        db.query(subscriptions.SubscriptionType)
        .where(subscriptions.SubscriptionType.id == request.subscription_type_id)
        .first()
    )
    if not sub_type:
        raise GenericException(
            code=status.HTTP_404_NOT_FOUND, message="Subscription type not exists"
        )

    current_date = datetime.now()
    active_sub = (
        db.query(subscriptions.Subscription)
        .filter(subscriptions.Subscription.user_id == current_user.id)
        .filter(subscriptions.Subscription.end_date > current_date)
        .first()
    )

    if active_sub:
        raise GenericException(
            code=status.HTTP_400_BAD_REQUEST, message="User already has an active subscription"
        )
    
    inactive_sub = (
        db.query(subscriptions.Subscription)
        .filter(subscriptions.Subscription.user_id == current_user.id)
        .filter(subscriptions.Subscription.end_date <= current_date)
        .first()
    )
    if inactive_sub:
        inactive_sub.start_date = current_date
        inactive_sub.end_date = current_date + timedelta(days=365)
        inactive_sub.subscription_type_id = request.subscription_type_id
        db.commit()
        db.refresh(inactive_sub)
        return current_user

    new_subscription = subscriptions.Subscription(
        user_id=current_user.id,
        subscription_type_id=request.subscription_type_id,
        start_date=current_date,
        end_date=current_date + timedelta(days=365)
    )

    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    db.refresh(current_user)

    return current_user
