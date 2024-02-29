from pydantic import BaseModel
from datetime import datetime
from typing_extensions import Optional


class TaskStatusCreate(BaseModel):
    """
    Model for creating a new TaskStatus.
    """
    task_status_name: str


class TaskCreate(BaseModel):
    """
    Model for creating a new Task.
    """
    project_id: int
    task_name: str
    task_description: str
    task_owner_id: int
    task_status_id: int


class TaskDetail(BaseModel):
    """
    Response model for TaskDetail.
    """
    task_id: int
    task_name: str
    task_description: str
    project_name: str
    project_description: str
    status_name: str
