from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from custom_exceptions.users_exceptions import GenericException
from models.users import User
from models.roles import Role
from utils.jwt_handler import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def get_user_by_email(db: Session, email: str) -> User:
    try:
        return db.query(User).filter(User.email == email).one()
    except NoResultFound:
        return None

def get_role_by_id(db: Session, role_id: int) -> Role:
    try:
        return db.query(Role).filter(Role.id == role_id).one()
    except NoResultFound:
        return None

def get_user_by_id(db: Session, user_id: int) -> User:
    try:
        return db.query(User).filter(User.id == user_id).one()
    except NoResultFound:
        raise GenericException(message="User not exists", code=status.HTTP_404_NOT_FOUND)

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token, "access")
    user_email = payload.get("sub")
    if user_email is None:
        raise GenericException(message="Invalid authentication credentials", code=status.HTTP_401_UNAUTHORIZED)
    return user_email
