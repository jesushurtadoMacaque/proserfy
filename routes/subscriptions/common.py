
from typing import List
from fastapi import APIRouter
from config.database import db_dependency
from models import subscriptions
from schemas import subscription_schema


router = APIRouter()

@router.get(
    "/subscriptions",
    tags=["subscription"],
    response_model=List[subscription_schema.SubscriptionTypeResponse],
)
def get_all_subscriptions(db: db_dependency):
    return db.query(subscriptions.SubscriptionType).all()
