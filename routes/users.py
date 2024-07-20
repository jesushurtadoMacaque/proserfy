from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from models.user import User, Role
from schemas.user_schema import RoleResponse, UserCreate, UserResponse, LoginForm, ChangeRoleRequest, SuspendUserRequest
from schemas.token_schema import Token
from config.database import SessionLocal
from typing import Annotated, List
from sqlalchemy.orm import Session
from utils.jwt_handler import create_access_token, verify_token
from passlib.context import CryptContext
from utils.password_handler import verify_password, hash_password

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    user_email = payload.get("sub")
    if user_email is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user_email

# ------ Routes ------
@router.post("/register", tags=["users"], response_model=Token, status_code=status.HTTP_201_CREATED)
async def create_users(user: UserCreate, db: db_dependency):
    hashed_password = hash_password(user.password)
    
    # Verificar si el rol especificado existe
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role does not exist")

    db_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hashed_password,
        receive_promotions=user.receive_promotions,
        role_id=user.role_id
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token = create_access_token(data={"sub": db_user.email})

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", tags=["users"], response_model=Token)
async def login_for_access_token(db: db_dependency, form_data: LoginForm):
    user = db.query(User).filter(User.email == form_data.email).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/{id}", tags=["users"], response_model=UserResponse)
async def read_user(id: int, db: db_dependency):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Roles management
@router.get("/roles", tags=["roles"], response_model=List[RoleResponse])
async def get_roles(db: db_dependency):
    roles = db.query(Role).all()
    return roles

@router.put("/users/change_role", tags=["users"], response_model=UserResponse)
async def change_user_role(db: db_dependency, request: ChangeRoleRequest, current_user: str = Depends(get_current_user)):
    user = db.query(User).filter(User.email == current_user).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    new_role = db.query(Role).filter(Role.id == request.role_id).first()
    if not new_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role specified",
        )

    user.role = new_role
    db.commit()
    return user

@router.put("/users/suspend", tags=["users"], response_model=UserResponse)
async def suspend_user(db: db_dependency, request: SuspendUserRequest, current_user: str = Depends(get_current_user)):
    user = db.query(User).filter(User.email == current_user).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.is_active = request.is_active
    db.commit()
    return user
