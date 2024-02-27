from pydantic import BaseModel


class UserRoleCreate(BaseModel):
    """
    Model for creating a new UserRole.
    """
    role_name: str