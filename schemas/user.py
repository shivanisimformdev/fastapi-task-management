from pydantic import BaseModel
from datetime import datetime


class CreateUserRequest(BaseModel):
    username: str
    email: str
    password_hash: str


class Token(BaseModel):
    access_token: str
    token_type: str


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