from fastapi import APIRouter, status
from config.database import db_dependency
from custom_exceptions.users_exceptions import GenericException
from models.versions import Version

router = APIRouter()

@router.get("/version", tags=["versions"])
def get_latest_version(db: db_dependency):
    version = db.query(Version).order_by(Version.release_date.desc()).first()
    if not version:
        raise GenericException(message="There is not versions", code=status.HTTP_404_NOT_FOUND)
    
    return {
        "version": version.version
    }
    


@router.get("/check-version", tags=["versions"])
def check_version(client_version: str, db: db_dependency):
    latest_version = get_latest_version(db)
    if(client_version != latest_version):
        return {
            "update_available": True,
            "latest_version": latest_version
        }
    else :
        return {
            "update_available": True
        }