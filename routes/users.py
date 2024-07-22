from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from custom_exceptions.users_esceptions import GenericException
from models.user import User, Role
from schemas.user_schema import RoleResponse, UserCreate, UserResponse, LoginForm, ChangeRoleRequest, SuspendUserRequest
from schemas.token_schema import Token
from config.database import SessionLocal
from typing import Annotated, List
from sqlalchemy.orm import Session
from utils.getters_handler import get_role_by_id, get_user_by_email, get_user_by_id
from utils.google_handlers import fetch_google_tokens, get_google_auth_url, verify_google_id_token
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
        raise GenericException(message="Invalid authentication credentials", code=status.HTTP_401_UNAUTHORIZED)
    return user_email

# ------ Routes ------
@router.post("/register", tags=["users"], response_model=Token, status_code=status.HTTP_201_CREATED)
async def create_users(user: UserCreate, db: db_dependency):
    if get_user_by_email(db, user.email):
        raise GenericException(message="Email already registered", code=status.HTTP_400_BAD_REQUEST)

    role = get_role_by_id(db, user.role_id)
    if not role: 
        raise GenericException(message="Role not exists", code=status.HTTP_404_NOT_FOUND)
    db_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=hash_password(user.password),
        receive_promotions=user.receive_promotions,
        role_id=role.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", tags=["users"], response_model=Token)
async def login_for_access_token(db: db_dependency, form_data: LoginForm):
    user = get_user_by_email(db, form_data.email)
    if not user.hashed_password:
        raise GenericException(message="Incorrect email or password", code=status.HTTP_401_UNAUTHORIZED)
    
    if not verify_password(form_data.password, user.hashed_password):
        raise GenericException(message="Incorrect email or password", code=status.HTTP_401_UNAUTHORIZED)

    elif not user.is_active:
        raise GenericException(message="Inactive user", code=status.HTTP_400_BAD_REQUEST)
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/{id}", tags=["users"], response_model=UserResponse)
async def read_user(id: int, db: db_dependency):
    user = get_user_by_id(db, id)
    if user:
        return user
    else :
        raise GenericException(message="User not exists", code=status.HTTP_404_NOT_FOUND)

@router.get("/roles", tags=["roles"], response_model=List[RoleResponse])
async def get_roles(db: db_dependency):
    return db.query(Role).all()

@router.put("/users/change_role", tags=["users"], response_model=UserResponse)
async def change_user_role(db: db_dependency, request: ChangeRoleRequest, current_user: str = Depends(get_current_user)):
    new_role = get_role_by_id(db, request.role_id)
    if new_role: 
        user = get_user_by_email(db, current_user)
        user.role = new_role
        db.commit()
        return user
    else : 
        raise GenericException(message="Role not exists", code=status.HTTP_404_NOT_FOUND)
        

@router.put("/users/suspend", tags=["users"], response_model=UserResponse)
async def suspend_user(db: db_dependency, request: SuspendUserRequest, current_user: str = Depends(get_current_user)):
    user = get_user_by_email(db, current_user)
    if user: 
        user.is_active = request.is_active
        db.commit()
        return user
    else :
        raise GenericException(message="User not exists", code=HTTP_404_NOT_FOUND)


# Google auth
@router.get("/login/google", tags=["users"])
async def google_login():
    auth_url = get_google_auth_url()
    return RedirectResponse(url=auth_url)

@router.get("/auth", tags=["users"], response_model=Token)
async def auth_callback(request: Request, db: db_dependency):
    code = request.query_params.get("code")
    if not code:
        raise GenericException(message="Authorization code not provided", code=status.HTTP_404_NOT_FOUND)

    token_response_data = fetch_google_tokens(code)
    
    if "error" in token_response_data:
        raise GenericException(message=token_response_data["error"], code=status.HTTP_400_BAD_REQUEST)

    id_token_str = token_response_data.get("id_token")
    if not id_token_str:
        raise GenericException(message="ID token not provided", code=status.HTTP_400_BAD_REQUEST)

    id_info = verify_google_id_token(id_token_str)
    user_email = id_info["email"]
    google_id = id_info["sub"]

    user = get_user_by_email(db, user_email)
    if not user:
        user = User(
            email=user_email,
            first_name=id_info.get("given_name", ""),
            last_name=id_info.get("family_name", ""),
            is_active=True,
            google_id=google_id,
            role_id=1  # Asigna un rol predeterminado, por ejemplo "Usuario"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if user.google_id != google_id:
            user.google_id = google_id
            db.commit()
            db.refresh(user)

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}