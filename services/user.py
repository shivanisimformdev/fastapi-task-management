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


def create_user(user: UserCreate, db):
    """
    Creates a new user with the provided user details in the database.
    """
    db_user = User(username=user.username, email=user.email)
    db_user.password_hash = hash_password(user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_details(user_id: int, db: Session = None):
    """
    Retrieves user details for the specified user ID.
    """
    if db is None:
        db = SessionLocal()
    user_detail = db.query(UserDetail).get(user_id)
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
    if db is None:
        db = SessionLocal()
    logger.info("Creating a new user role with name: %s", user_role.role_name)
    new_user_role = UserRole(**user_role.dict())
    db.add(new_user_role)
    db.commit()
    db.refresh(new_user_role)
    logger.info("User role created successfully with ID: %d", new_user_role.user_role_id)
    return new_user_role


def create_user_technology(user_technology: UserTechnologyCreate, db: Session = None):
    """
    Creates a new user technology with the provided technology details in the database.
    """
    if db is None:
        db = SessionLocal()
    logger.info("Creating a new user technology with name: %s", user_technology.technology_name)
    new_user_technology = UserTechnology(**user_technology.dict())
    db.add(new_user_technology)
    db.commit()
    db.refresh(new_user_technology)
    logger.info("User technology created successfully with ID: %d", new_user_technology.user_technology_id)
    return new_user_technology


def create_user_details(user_details: UserDetailsCreate, db: Session = None):
    """
    Creates a new user detail entry with the provided user details in the database.
    """
    if db is None:
        db = SessionLocal()
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
    new_user_detail = UserDetail(**user_details.dict())

    db.add(new_user_detail)
    db.commit()
    db.refresh(new_user_detail)

    logger.info("User detail entry created successfully with ID: %d", new_user_detail.id)
    return new_user_detail
