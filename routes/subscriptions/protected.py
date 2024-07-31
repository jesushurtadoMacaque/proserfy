from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status
from config.database import db_dependency
from custom_exceptions.users_exceptions import GenericException
from models import subscriptions
from models.users import User
from routes.professional_services.protected import get_current_active_user
from schemas import subscription_schema
from schemas.user_schema import UserResponse

router = APIRouter()

@router.post("/subscription", tags=["subscription"], response_model=UserResponse)
def adding_user_sub(
    request: subscription_schema.SubscriptionCreate,
    db: db_dependency,
    current_user: User = Depends(get_current_active_user),
):
    # Verificar si el tipo de suscripción existe
    sub_type = db.query(subscriptions.SubscriptionType).get(request.subscription_type_id)
    if not sub_type:
        raise GenericException(
            code=status.HTTP_404_NOT_FOUND, message="Subscription type not exists"
        )

    current_date = datetime.now()

    # Buscar si el usuario tiene una suscripción activa o inactiva
    user_subscription = (
        db.query(subscriptions.Subscription)
        .filter(subscriptions.Subscription.user_id == current_user.id)
        .first()
    )

    # Si hay una suscripción activa, lanzar excepción
    if user_subscription and user_subscription.end_date > current_date:
        raise GenericException(
            code=status.HTTP_400_BAD_REQUEST, message="User already has an active subscription"
        )

    # Si hay una suscripción inactiva, actualizar fechas
    if user_subscription and user_subscription.end_date <= current_date:
        user_subscription.start_date = current_date
        user_subscription.end_date = current_date + timedelta(days=365)
        user_subscription.subscription_type_id = request.subscription_type_id
        db.commit()
        db.refresh(user_subscription)
    else:
        # Crear nueva suscripción si no hay ninguna
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