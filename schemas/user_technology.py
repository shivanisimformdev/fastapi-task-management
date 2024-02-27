from pydantic import BaseModel


class UserTechnologyCreate(BaseModel):
    """
    Model for creating a new UserTechnology.
    """
    technology_name: str