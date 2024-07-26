from routes.professional_services import common, protected
from fastapi import APIRouter

router = APIRouter()


router.include_router(common.router)
router.include_router(protected.router)



    
