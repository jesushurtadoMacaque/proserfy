from fastapi import APIRouter
from routes.users import common, protected

router = APIRouter()

router.include_router(common.router)
router.include_router(protected.router)
