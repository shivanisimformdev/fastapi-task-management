import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Type, Union
from sqlalchemy.orm import Session
from fastapi import HTTPException
load_dotenv()
from logger import logger


# Constructing SQLite database URL
URL_DATABASE = "sqlite:///./sqlite_db.db"
# URL_DATABASE = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Function to yield a database session.

    Yields:
        Session: SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def commit_db(db: Session, new_instance) -> Type:
    try:
        db.add(new_instance)
        db.commit()
        db.refresh(new_instance)
        return new_instance
    except Exception:
        logger.error("Error occurred while creating instance")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create instance")


def get_db_session(db: Session = None) -> Session:
    return db if db else SessionLocal()
