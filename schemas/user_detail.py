from pydantic import BaseModel
from datetime import datetime


class UserProfilesCreate(BaseModel):
    """
    Model for creating UserProfiles.
    """
    user_id: int
    user_role_id: int
    user_technology_id: int


class UserProfileResponse(BaseModel):
    """
    Response model for UserProfile.
    """
    id: int
    created_at: datetime
    role_name: str
    technology_name: str
