from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str
    email: str
    password_hash: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []


class GetUser(BaseModel):
    """
    Model for getting user details.
    """
    email: str
    password: str
