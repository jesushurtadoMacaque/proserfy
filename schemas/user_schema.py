from pydantic import BaseModel, EmailStr, Field
from models import subscriptions
from datetime import date
from typing import List, Optional
from datetime import datetime

from schemas.subscription_schema import SubscriptionResponse

class RoleBase(BaseModel):
    name: str


class RoleResponse(RoleBase):
    id: int

    class Config:
        from_attributes = True


class ChangeRoleRequest(BaseModel):
    role_id: int


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=8, max_length=255)
    new_password: str = Field(..., min_length=8, max_length=255)


class CompleteProfile(BaseModel):
    birth_date: date


class SuspendUserRequest(BaseModel):
    is_active: bool


class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr = Field(...)
    birth_date: date = Field(...)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=255)
    receive_promotions: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    role_id: int = Field(...)


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    receive_promotions: Optional[bool] = None


class UserExternalCreate(UserBase):
    apple_id: Optional[str] = None
    facebook_id: Optional[str] = None
    google_id: Optional[str] = None
    receive_promotions: bool = False


class UserResponse(UserBase):
    id: int
    receive_promotions: bool
    apple_id: Optional[str] = None
    facebook_id: Optional[str] = None
    google_id: Optional[str] = None
    is_active: bool
    role: RoleResponse
    subscription: Optional[SubscriptionResponse]
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True


class LoginForm(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True
