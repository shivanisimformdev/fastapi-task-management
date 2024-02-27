from pydantic import BaseModel
from datetime import datetime


class ProjectCreate(BaseModel):
    """
    Model for creating a new Project.
    """
    project_name: str
    project_description: str
    created_by_id: int


class ProjectResponse(BaseModel):
    """
    Response model for Project.
    """
    project_id: int
    project_name: str
    project_description: str
    created_at: datetime
    updated_at: datetime
    created_by_id: int


class UserProjectCreate(BaseModel):
    """
    Model for creating a new UserProject.
    """
    user_id: int
    project_id: int
