from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from database.session import get_db

from schemas.user_role import UserRoleCreate
from schemas.user_detail import UserProfileResponse, UserProfilesCreate
from schemas.user_technology import UserTechnologyCreate
from services.user import (
    get_user_details,
    create_user_technology,
    create_user_role,
    create_user_details
)


router = APIRouter(prefix="/users", tags=['users'])


@router.get("/{user_id}/details", response_model=UserProfileResponse)
def get_user_details_api(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves user details for the specified user ID.
    """
    return get_user_details(user_id)


@router.post("/user_roles/")
def create_user_role_api(user_role: UserRoleCreate, db: Session = Depends(get_db)):
    """
    Creates a new user role with the provided role details in the database.

    """
    return create_user_role(user_role, db)  


@router.post("/user_technologies/")
def create_user_technology_api(user_technology: UserTechnologyCreate, db: Session = Depends(get_db)):
    """
    Creates a new user technology with the provided technology details in the database.

    """
    return create_user_technology(user_technology, db)


@router.post("/user_details/")
def create_user_details_api(user_details: UserProfilesCreate, db: Session = Depends(get_db)):
    """
    Creates a new user detail entry with the provided user details in the database.

    Args:
        user_details (UserProfilesCreate): Details of the user to be created.

    Returns:
        UserProfiles: Newly created user detail object.

    Raises:
        HTTPException: If user, user role, or user technology not found.

    """
    """
    Creates a new user detail entry with the provided user details in the database.
    """
    return create_user_details(user_details, db)
