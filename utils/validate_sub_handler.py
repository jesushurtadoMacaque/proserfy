

from datetime import datetime
from fastapi import Depends, status
from custom_exceptions.users_exceptions import GenericException
from models.subscriptions import Subscription
from models.users import User
from routes.professional_services.protected import get_current_active_user
from config.database import db_dependency


def verify_active_subscription(db:db_dependency, current_user: User = Depends(get_current_active_user)):
    current_date = datetime.now()
    active_subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == current_user.id)
        .filter(Subscription.end_date > current_date)
        .first()
    )
    if not active_subscription:
        raise GenericException(
            code=status.HTTP_403_FORBIDDEN,
            message="User does not have an active subscription"
        )
    return current_user
