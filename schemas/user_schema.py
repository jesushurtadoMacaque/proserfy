from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RoleBase(BaseModel):
    name: str

class RoleResponse(RoleBase):
    id: int

    class Config:
        orm_mode = True

class ChangeRoleRequest(BaseModel):
    role_id: int

class SuspendUserRequest(BaseModel):
    is_active: bool

class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=255)
    receive_promotions: bool = False
    role_id: int = Field(...)

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

    class Config:
        orm_mode = True

class LoginForm(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


#@field_validator("password")
#def validate_password(cls, v):
#    if len(v) < 8:
#            raise ValueError('Password must be at least 8 characters long')
#    return v