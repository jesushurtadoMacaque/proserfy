from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator, validator
from datetime import date, time
from typing import Optional, List
from schemas.user_schema import UserResponse


class CategoryBase(BaseModel):
    name: str


class CategoryResponse(CategoryBase):
    id: int

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

class WorkScheduleBase(BaseModel):
    day_of_week: str
    start_time: time
    end_time: time
    is_active: bool = True
    
    @field_validator('start_time', 'end_time')
    def validate_time(cls, v):
        if not isinstance(v, time):
            raise ValueError('Must be a valid time')
        return v

    @field_validator('end_time')
    def validate_time_order(cls, v, info: ValidationInfo):
        start_time = info.data.get('start_time')
        if start_time and v <= start_time:
            raise ValueError('end_time must be after start_time')
        return v

class WorkScheduleCreate(WorkScheduleBase):
    pass

class WorkScheduleResponse(WorkScheduleBase):
    id: int

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
    city: str
    range_from: int
    range_to: int
    latitude: float
    longitude: float
    subcategory_id: int

    @field_validator('range_to')
    def validate_range(cls, v, info: ValidationInfo):
        range_from = info.data.get('range_from')
        if range_from and v < range_from:
            raise ValueError('range_to must be greater than or equal to range_from')
        return v

class ProfessionalServiceCreate(ProfessionalServiceBase):
    work_schedules: List[WorkScheduleCreate]  


class ProfessionalServiceResponse(ProfessionalServiceBase):
    id: int
    average_rating: float
    professional: UserResponse
    subcategory: SubCategoryResponse
    images: List[ServiceImageResponse]
    work_schedules: List[WorkScheduleResponse]

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
