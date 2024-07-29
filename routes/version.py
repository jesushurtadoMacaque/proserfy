from fastapi import APIRouter
from routes.versions import common

router = APIRouter()

router.include_router(common.router)