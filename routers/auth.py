from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing_extensions import Annotated
#TODO typing and some other packages are not refected in requirements.txt
from sqlalchemy import or_
from pydantic import ValidationError

from sqlalchemy.orm import Session
from datetime import timedelta
from jose import jwt, JWTError
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, SecurityScopes
from database.session import get_db
from schemas.user import CreateUserRequest, Token, TokenData
from models.user import User
from utils.jwt import create_access_token, authenticate_user, get_user
from constants.keys import SECRET_KEY, ALGORITHM
from routers.logger import logger
from services.user import create_user

router = APIRouter(prefix="/auth", tags=['auth'])

templates = Jinja2Templates(directory="templates")


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token",
                                     scopes={"admin": "Admin access", "user": "Authenticated user access"})


#TODO below APIs are using async, is it required?
#TODO this code is same as in user.py. If we don't need to use this API, remove this code.
# @router.post("/register/", response_class=HTMLResponse)
# def register_user(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
#     # create_user_model = User(
#     #     username=create_user_request.username,
#     #     email=create_user_request.email,
#     #     password_hash=bcrypt_context.hash(create_user_request.password_hash)
#     # )
#     # db.add(create_user_model)
#     # db.commit()
#     # db.refresh(create_user_model)
#     # return {
#     #     "email": create_user_model.email,
#     #     "username": create_user_model.username
#     # }
#     user = db.query(User).filter(or_(User.username == username, User.email == email)).first()
#     # if user:
#     #     return templates.TemplateResponse("register.html", {"request": request, "username": user.username, "message":"User already exist"})
#     logger.info("Creating a new user with username: %s and email: %s", username, email)
#     user = create_user(username, password, email, db)
#     return templates.TemplateResponse("login.html", {"request": request, "username": user.username, "message":"User registered succsessfully"})


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could Not Validate User.")
    token = create_access_token(username=user.username, user_id=user.id, expire_delta=timedelta(minutes=20), scope=["admin"] if user.is_admin_user else ["user"])
    return {
        'access_token': token,
        'token_type': 'bearer'
    }


def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        scope: str = payload.get("scope")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
        return {"username": username, "id": user_id, "scope": scope}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")


def get_scope_user(
        security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_bearer)], db: User = Depends(get_db)
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scope", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = get_user(db=db, username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user, token_data.scopes
