from pydantic import AnyHttpUrl, BaseModel
from typing import List, Optional
from schemas.profesional_service_schema import ProfessionalServiceResponse


class PaginatedResponse(BaseModel):
    total_items: int
    total_pages: int
    current_page: AnyHttpUrl
    next_page: Optional[AnyHttpUrl]
    prev_page: Optional[AnyHttpUrl]
    items: List[ProfessionalServiceResponse]
