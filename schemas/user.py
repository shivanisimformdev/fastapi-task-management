from pydantic import BaseModel
from datetime import datetime
from typing_extensions import Union, List

from models.user import User


class CreateUserRequest(BaseModel):
    """
    Model for creating a new User request.
    """
    username: str
    email: str
    password_hash: str


class Token(BaseModel):
    """
    Model for returning token response.
    """
    access_token: str
    token_type: str
    user_id: int


class TokenData(BaseModel):
    username: Union[str, None] = None
    scopes: List[str] = []


class UserCreate(BaseModel):
    """
    Model for creating a new User.
    """
    username: str
    email: str
    password: str


class GetUser(BaseModel):
    """
    Model for getting user details.
    """
    email: str
    password: str
