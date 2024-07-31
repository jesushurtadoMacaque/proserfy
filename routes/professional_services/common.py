from fastapi import APIRouter, Query, Request, status
from sqlalchemy import text
from custom_exceptions.users_exceptions import GenericException
from models.professional_services import ProfessionalService
from schemas.paginated_schema import PaginatedResponse
from config.database import db_dependency
from utils.generate_url import build_pagination_urls


router = APIRouter()


@router.get(
    "/professional-services",
    tags=["professional_services"],
    response_model=PaginatedResponse,
)
async def get_professional_services(
    db: db_dependency,
    request: Request,
    limit: int = Query(15),
    offset: int = Query(0),
):
    try:
        query = db.query(ProfessionalService)
        total = query.count()
        services = query.limit(limit).offset(offset).all()

        total_pages = (total + limit - 1) // limit

        current_page_url, next_page_url, prev_page_url = build_pagination_urls(
            request, offset, limit, total
        )

        return PaginatedResponse(
            total_items=total,
            total_pages=total_pages,
            current_page=current_page_url,
            next_page=next_page_url,
            prev_page=prev_page_url,
            items=services,
        )
    except Exception as exc:
        raise GenericException(
            message="Something went wrong", code=status.HTTP_400_BAD_REQUEST
        )


@router.get(
    "/professional-services/filter",
    name="Get services by location range",
    tags=["professional_services"],
    response_model=PaginatedResponse,
)
def get_services(
    db: db_dependency,
    request: Request,
    limit: int = Query(15),
    offset: int = Query(0),
    lat: float = Query(...),
    lon: float = Query(...),
    range_km: float = Query(...),
):

    try:
        query = (
            db.query(ProfessionalService)
            .filter(
                text(
                    "ST_Distance_Sphere(point(longitude, latitude), point(:lon, :lat)) <= :range_km * 1000"
                )
            )
            .params(lon=lon, lat=lat, range_km=range_km)
        )

        total = query.count()

        services = query.limit(limit).offset(offset).all()
        total_pages = (total + limit - 1) // limit

        current_page_url, next_page_url, prev_page_url = build_pagination_urls(
            request, offset, limit, total
        )

        return PaginatedResponse(
            total_items=total,
            total_pages=total_pages,
            current_page=current_page_url,
            next_page=next_page_url,
            prev_page=prev_page_url,
            items=services,
        )
    except Exception as exc:
        raise GenericException(
            message="Something went wrong", code=status.HTTP_400_BAD_REQUEST
        )
