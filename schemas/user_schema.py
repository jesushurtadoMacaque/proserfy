from pydantic import BaseModel, EmailStr
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
    first_name: str
    last_name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    receive_promotions: bool = False
    role_id: int

class UserExternalCreate(UserBase):
    apple_id: Optional[str] = None
    facebook_id: Optional[str] = None
    google_id: Optional[str] = None
    receive_promotions: bool = False
    role_id: int

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
