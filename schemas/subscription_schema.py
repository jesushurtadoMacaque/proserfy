from pydantic import BaseModel
from datetime import datetime

class SubscriptionTypeBase(BaseModel):
    name: str
    price: float

class SubscriptionTypeCreate(SubscriptionTypeBase):
    pass

class SubscriptionTypeResponse(SubscriptionTypeBase):
    id: int

    class Config:
        from_attributes = True

class SubscriptionBase(BaseModel):
    start_date: datetime
    end_date: datetime

class SubscriptionCreate(BaseModel):
    subscription_type_id: int

class SubscriptionResponse(SubscriptionBase):
    id: int
    subscription_type: SubscriptionTypeResponse

    class Config:
        from_attributes = True
