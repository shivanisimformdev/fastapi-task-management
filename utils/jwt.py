# jwt.py
from datetime import datetime, timedelta
from jose import jwt, JWTError
from models.user import User
from passlib.context import CryptContext
from constants.keys import SECRET_KEY, ALGORITHM
from sqlalchemy.orm import Session

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")


def create_access_token(username: str, user_id: int, expire_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expire_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password_hash):
        return False
    return user
