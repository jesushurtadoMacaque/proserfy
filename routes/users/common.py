from fastapi import APIRouter, Cookie, Response, status, Request
from fastapi.responses import RedirectResponse
from jose import JWTError
from custom_exceptions.users_exceptions import GenericException
from models.users import User
from models.roles import Role
from schemas.user_schema import RoleResponse, UserCreate, UserResponse, LoginForm
from schemas.token_schema import Token
from config.database import db_dependency
from typing import List
from utils.error_handler import validation_error_response
from utils.getters_handler import get_role_by_id, get_user_by_email, get_user_by_id
from utils.google_handlers import fetch_google_tokens, get_google_auth_url, verify_google_id_token
from utils.jwt_handler import create_access_token, create_refresh_token, verify_token
from utils.password_handler import verify_password, hash_password

router = APIRouter()

@router.post("/register", tags=["users"], response_model=Token, responses=validation_error_response,status_code=status.HTTP_201_CREATED)
async def create_users(user: UserCreate, db: db_dependency, response: Response):
        
    if get_user_by_email(db, user.email):
        raise GenericException(message="Email already registered", code=status.HTTP_400_BAD_REQUEST)

    role = get_role_by_id(db, user.role_id)
    if not role: 
        raise GenericException(message="Role not exists", code=status.HTTP_404_NOT_FOUND)
        
    db_user = User(**user.model_dump())
    db_user.password = hash_password(user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
        
    return {"access_token": access_token}
 
@router.post("/login", tags=["users"], response_model=Token, responses=validation_error_response)
async def login_for_access_token(db: db_dependency, form_data: LoginForm, response: Response):
    
    user = get_user_by_email(db, form_data.email)
        
    if not user or not user.password or not verify_password(form_data.password, user.password):
        raise GenericException(message="Incorrect email or password", code=status.HTTP_401_UNAUTHORIZED)

    elif not user.is_active:
        raise GenericException(message="User is suspended", code=status.HTTP_400_BAD_REQUEST)
        
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return {"access_token": access_token}
    
@router.get("/users/{id}", tags=["users"], response_model=UserResponse, responses=validation_error_response)
async def read_user(id: int, db: db_dependency):
    
    user = get_user_by_id(db, id)
    if user:
        return user
    else :
        raise GenericException(message="User not exists", code=status.HTTP_404_NOT_FOUND)
   
@router.get("/roles", tags=["roles"], response_model=List[RoleResponse], responses=validation_error_response)
async def get_roles(db: db_dependency):
    try:
        return db.query(Role).all()
    except Exception as exc:
        raise GenericException(message="Something went wrong", code=status.HTTP_400_BAD_REQUEST)    

@router.post("/refresh", tags=["users"], response_model=Token, responses=validation_error_response)
async def refresh_access_token(refresh_token: str = Cookie(...)):
    try:
        payload = verify_token(refresh_token, "refresh")
        user_email = payload.get("sub")

        access_token = create_access_token(data={"sub": user_email})
        
        return {"access_token": access_token}

    except JWTError:
        raise GenericException(message="Invalid refresh token", code=status.HTTP_401_UNAUTHORIZED)
    
# Google auth
@router.get("/login/google", tags=["users"])
async def google_login():
    try:
        auth_url = get_google_auth_url()
        print("*******auth_url********")
        print(auth_url)
        return RedirectResponse(url=auth_url)
    
    except Exception as exc:
        raise GenericException(message="Something went wrong", code=status.HTTP_400_BAD_REQUEST)

@router.get("/auth", tags=["users"], name="Google callback" , response_model=Token, responses=validation_error_response)
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
            birth_date=id_info.get("birthday"),
            is_active=True,
            google_id=google_id,
            role_id=1
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
    refresh_token = create_refresh_token(data={"sub": user.email})

    return {"access_token": access_token, "refresh_token": refresh_token,"token_type": "bearer"}
    
