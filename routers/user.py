from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from models.user import UserDetail, UserRole, UserTechnology, User

from database.session import get_db
from routers.logger import logger
from schemas.user import UserCreate, GetUser
from schemas.user_role import UserRoleCreate
from schemas.user_detail import UserDetailResponse, UserDetailsCreate
from schemas.user_technology import UserTechnologyCreate
from utils.hash_pwd import hash_password
from utils.verify_pwd import verify_password
from services.user import get_user_details, create_user, create_user_technology, create_user_role, create_user_details

router = APIRouter(prefix="/users", tags=['users'])


def get_user_by_email_and_password(email: str, password: str, db: Session):

    """
    Retrieves a user by email and password from the database session.
    Returns:
        User: Retrieved user object.

    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        logger.warning("Failed login attempt for given email")
        raise HTTPException(status_code=404, detail="User not found or invalid credentials")
    return user


@router.post("/")
def create_user_route(user: UserCreate, db: Session = Depends(get_db)):
    """
        Creates a new user with the provided user details in the database.
    """
    return create_user(user, db)


@router.post("/login")
def login_user(user: GetUser, db: Session = Depends(get_db)):
    user = get_user_by_email_and_password(user.email, user.password, db)
    return user


@router.get("/{user_id}/details", response_model=UserDetailResponse)
def get_user_details_route(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves user details for the specified user ID.
    """
    return get_user_details(user_id)


@router.post("/user_roles/")
def create_user_role_route(user_role: UserRoleCreate, db: Session = Depends(get_db)):
    """
    Creates a new user role with the provided role details in the database.

    """
    return create_user_role(user_role, db)  


@router.post("/user_technologies/")
def create_user_technology_route(user_technology: UserTechnologyCreate, db: Session = Depends(get_db)):
    """
    Creates a new user technology with the provided technology details in the database.

    """
    return create_user_technology(user_technology, db)


@router.post("/user_details/")
def create_user_details_route(user_details: UserDetailsCreate, db: Session = Depends(get_db)):
    """
    Creates a new user detail entry with the provided user details in the database.

    Args:
        user_details (UserDetailsCreate): Details of the user to be created.

    Returns:
        UserDetails: Newly created user detail object.

    Raises:
        HTTPException: If user, user role, or user technology not found.

    """
    """
    Creates a new user detail entry with the provided user details in the database.
    """
    return create_user_details(user_details, db)
