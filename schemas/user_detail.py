from pydantic import BaseModel
from datetime import datetime


class UserDetailsCreate(BaseModel):
    """
    Model for creating UserDetails.
    """
    user_id: int
    user_role_id: int
    user_technology_id: int


class UserDetailResponse(BaseModel):
    """
    Response model for UserDetail.
    """
    id: int
    created_at: datetime
    role_name: str
    technology_name: str
