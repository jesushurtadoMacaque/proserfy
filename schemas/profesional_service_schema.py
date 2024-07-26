from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional, List

from schemas.user_schema import UserResponse

class CategoryBase(BaseModel):
    name: str

class CategoryResponse(CategoryBase):
    id: int
    #subcategories: List["SubCategoryResponse"]

    class Config:
        from_attributes = True

class SubCategoryBase(BaseModel):
    name: str
    category_id: int

class SubCategoryResponse(SubCategoryBase):
    id: int
    category: CategoryResponse

    class Config:
        from_attributes = True

class ServiceImageBase(BaseModel):
    url: str

class ServiceImageCreate(ServiceImageBase):
    service_id: int

class ServiceImageResponse(ServiceImageBase):
    id: int

    class Config:
        from_attributes = True

class ProfessionalServiceBase(BaseModel):
    name: str
    description: str
    location: str
    latitude: float
    longitude: float
    subcategory_id: int

class ProfessionalServiceCreate(ProfessionalServiceBase):
    pass

class ProfessionalServiceResponse(ProfessionalServiceBase):
    id: int
    average_rating: float
    professional: UserResponse
    subcategory: SubCategoryResponse
    images: List[ServiceImageResponse]  

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    text: str
    user_id: int
    professional_service_id: int

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    user: UserResponse
    professional_service: ProfessionalServiceResponse

    class Config:
        from_attributes = True

class RatingBase(BaseModel):
    rating: float
    user_id: int
    professional_service_id: int

class RatingCreate(RatingBase):
    pass

class RatingResponse(RatingBase):
    id: int
    user: UserResponse
    professional_service: ProfessionalServiceResponse

    class Config:
        from_attributes = True

class ImageUpdatedResponse(BaseModel):
    detail: str
    uploaded_files: List[str]
    errors: List[str]