from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from models.user import Role, User

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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Role not exists")
