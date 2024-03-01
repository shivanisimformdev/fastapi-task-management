from models.user import User
from utils.hash_pwd import hash_password
from schemas.user import UserCreate
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.user import UserDetail, UserRole, UserTechnology
from schemas.user_role import UserRoleCreate
from schemas.user_technology import UserTechnologyCreate
from schemas.user_detail import UserDetailsCreate
from database.session import SessionLocal
from routers.logger import logger


def create_user(username: str, password: str, email: str, is_admin_user: str, db: Session = None):
    """
    Creates a new user with the provided user details in the database.
    """
    if db is None:
        db = SessionLocal()

    db_user = User(username=username, email=email, is_admin_user=True if is_admin_user == "Yes" else False)
    db_user.password_hash = hash_password(password)  # You would need to implement hash_password function
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info("User created successfully with ID: %d", db_user.id)
    return db_user

def create_details_of_user(user_id: int, user_role_id: int, user_technology_id: int, db: Session = None):
    """
    Creates a new user detail entry with the provided user details in the database.
    """
    if db is None:
        db = SessionLocal()

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error("User not found with ID: %d", user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_role = db.query(UserRole).filter(UserRole.user_role_id == user_role_id).first()
    if not user_role:
        logger.error("User role not found with ID: %d", user_role_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User role not found")
    user_technology = db.query(UserTechnology).filter(UserTechnology.user_technology_id == user_technology_id).first()
    if not user_technology:
        logger.error("User technology not found with ID: %d", user_technology_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User technology not found")
    new_user_detail = UserDetail(user_id=user_id, user_role_id=user_role_id, user_technology_id=user_technology_id)
    db.add(new_user_detail)
    db.commit()
    db.refresh(new_user_detail)
    logger.info("User detail entry created successfully with ID: %d", new_user_detail.id)
    user_detail = db.query(UserDetail, UserRole.role_name, UserTechnology.technology_name).join(UserRole,
    UserDetail.user_role_id == UserRole.user_role_id).join(UserTechnology,
    UserDetail.user_technology_id == UserTechnology.user_technology_id).filter(UserDetail.user_id == user_id).order_by(UserDetail.id.desc()).first()
    return user, user_detail


def get_details_of_user(user_id: int, db: Session = None):
    """
    Retrieves user details for the specified user ID.
    """
    if db is None:
        db = SessionLocal()

    user_detail = db.query(UserDetail).filter(user_id == user_id).first()
    if not user_detail:
        logger.error(f"User detail of given user id {user_id} does not exist")

    user = db.query(User).filter(User.id == user_id).first()
    user_detail = db.query(UserDetail, UserRole.role_name, UserTechnology.technology_name).join(UserRole,
    UserDetail.user_role_id == UserRole.user_role_id).join(UserTechnology,
    UserDetail.user_technology_id == UserTechnology.user_technology_id).filter(UserDetail.user_id == user_id).order_by(UserDetail.id.desc()).first()
    logger.info("User details retrieved successfully for user ID: %d", user_id)
    return user, user_detail


def create_user_role_data(role_name: str, db: Session = None):
    """
    Creates a new user role with the provided role details in the database.
    """
    if db is None:
        db = SessionLocal()
    logger.info("Creating a new user role with name: %s", role_name)
    new_user_role = UserRole(role_name=role_name)
    db.add(new_user_role)
    db.commit()
    db.refresh(new_user_role)
    logger.info("User role created successfully with ID: %d", new_user_role.user_role_id)
    return


def create_user_technology_data(technology_name: str, db: Session = None):
    """
    Creates a new user technology with the provided technology details in the database.
    """
    if db is None:
        db = SessionLocal()
    logger.info("Creating a new user technology with name: %s", technology_name)
    new_user_technology = UserTechnology(technology_name=technology_name)
    db.add(new_user_technology)
    db.commit()
    db.refresh(new_user_technology)
    logger.info("User technology created successfully with ID: %d", new_user_technology.user_technology_id)
    return new_user_technology
