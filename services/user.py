from models.user import User
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.user import UserProfile, UserRole, UserTechnology
from schemas.user_role import UserRoleCreate
from schemas.user_technology import UserTechnologyCreate
from schemas.user_detail import UserProfilesCreate
from database.session import SessionLocal, get_db_session, commit_db
from logger import logger


def get_user_details(user_id: int, db: Session = None):
    """
    Retrieves user details for the specified user ID.
    """
    if db is None:
        db = SessionLocal()
    user_detail = db.query(UserProfile).get(user_id)

    if not user_detail:
        raise HTTPException(status_code=404, detail="User details not found")
    user_role = db.query(UserRole).filter(UserRole.user_role_id == user_detail.user_role_id).first()
    user_technology = db.query(UserTechnology).filter(UserTechnology.user_technology_id == user_detail.user_technology_id).first()

    return {
        "id": user_detail.id,
        "created_at": user_detail.created_at,
        "role_name": user_role.role_name,
        "technology_name": user_technology.technology_name
    }


def create_user_role(user_role: UserRoleCreate, db: Session = None):
    """
    Creates a new user role with the provided role details in the database.
    """
    db = get_db_session(db)
    logger.info("Creating a new user role with name: %s", user_role.role_name)
    new_user_role = UserRole(**user_role.dict())
    new_user_role = commit_db(db, new_user_role)
    logger.info("User role created successfully with ID: %d", new_user_role.user_role_id)
    return new_user_role


def create_user_technology(user_technology: UserTechnologyCreate, db: Session = None):
    """
    Creates a new user technology with the provided technology details in the database.
    """
    db = get_db_session(db)
    logger.info("Creating a new user technology with name: %s", user_technology.technology_name)
    new_user_technology = UserTechnology(**user_technology.dict())
    new_user_technology = commit_db(db, new_user_technology)
    logger.info("User technology created successfully with ID: %d", new_user_technology.user_technology_id)
    return new_user_technology


def create_user_details(user_details: UserProfilesCreate, db: Session = None):
    """
    Creates a new user detail entry with the provided user details in the database.
    """
    db = get_db_session()
    logger.info("Creating a new user detail entry with user_id: %d", user_details.user_id)
    user = db.query(User).filter(User.id == user_details.user_id).first()
    if not user:
        logger.error("User not found with ID: %d", user_details.user_id)
        raise HTTPException(status_code=404, detail="User not found")
    user_role = db.query(UserRole).filter(UserRole.user_role_id == user_details.user_role_id).first()
    if not user_role:
        logger.error("User role not found with ID: %d", user_details.user_role_id)
        raise HTTPException(status_code=404, detail="User role not found")
    user_technology = db.query(UserTechnology).filter(UserTechnology.user_technology_id == user_details.user_technology_id).first()
    if not user_technology:
        logger.error("User technology not found with ID: %d", user_details.user_technology_id)
        raise HTTPException(status_code=404, detail="User technology not found")
    new_user_detail = UserProfile(**user_details.dict())

    new_user_detail = commit_db(new_user_detail)

    logger.info("User detail entry created successfully with ID: %d", new_user_detail.id)
    return new_user_detail
