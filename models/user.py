from database.base import Base
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, Boolean


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_admin_user = Column(Boolean, default=False)


class UserTechnology(Base):
    __tablename__ = "user_technologies"
    user_technology_id = Column(Integer, primary_key=True, index=True)
    technology_name = Column(String)


class UserRole(Base):
    __tablename__ = "user_roles"
    user_role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String)


class UserDetail(Base):
    __tablename__ = "user_details"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user_role_id = Column(Integer, ForeignKey('user_roles.user_role_id'))
    user_technology_id = Column(Integer, ForeignKey('user_technologies.user_technology_id'))
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", backref="user_details")
    user_role = relationship("UserRole", backref="user_details")
    user_technology = relationship("UserTechnology", backref="user_details")
