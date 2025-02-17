from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional
from schemas.subscription_schema import SubscriptionBoughtHistoryBase, SubscriptionResponse, SubscriptionTypeResponse

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

class ProfileImageBase(BaseModel):
    url: str

class ProfileImageCreate(ProfileImageBase):
    user_id: int

class ProfileImageResponse(ProfileImageBase):
    id: int

    class Config:
        from_attributes = True

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
    profile_image: Optional[ProfileImageResponse]
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True

class SubscriptionBoughtHistoryResponse(SubscriptionBoughtHistoryBase):
    user: UserResponse
    subscription_type: SubscriptionTypeResponse

class LoginForm(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True
