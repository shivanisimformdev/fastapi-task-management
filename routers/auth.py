from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing_extensions import Annotated
#TODO typing and some other packages are not refected in requirements.txt
from sqlalchemy import or_
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import jwt, JWTError
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from database.session import get_db
from schemas.user import CreateUserRequest, Token
from models.user import User
from utils.jwt import create_access_token, authenticate_user
from constants.keys import SECRET_KEY, ALGORITHM
from .logger import logger
from services.user import create_user

router = APIRouter(prefix="/auth", tags=['auth'])

templates = Jinja2Templates(directory="templates")


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


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
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {
        'access_token': token,
        'token_type': 'bearer'
    }


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                details="Could not validate user.")
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
