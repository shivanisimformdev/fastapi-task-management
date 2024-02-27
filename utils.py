from datetime import timedelta, datetime
from typing import Optional, Union, Any
import bcrypt
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

# Security configurations
JWT_REFRESH_SECRET_KEY = '{`,*}Z&`;}Rju?e/~$@}xgvPv`w>5Yj_4Y{Rqjm|o#uMh3=CxvM$x$+,))`>@&(#'
SECRET_KEY = 'q2SY3?JCNz2&,YeOmgd^wGCoP"vSjw-*XvNC7qhgdbt&ZJ;%&kF3Z~e{RDAaJ8'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Sample database (replace it with your database in real application)
fake_users_db = {}


def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


# Function to authenticate user
def authenticate_user(fake_db, username: str, password: str):
    user = fake_db.get(username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user
