from database import Base
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)


class UserTechnology(Base):
    __tablename__ = "user_technologies"
    user_technology_id = Column(Integer, primary_key=True, index=True)
    technology_name = Column(String)


class UserRole(Base):
    __tablename__ = "user_roles"
    user_role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String)


class UserDetails(Base):
    __tablename__ = "user_details"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user_role_id = Column(Integer, ForeignKey('user_roles.user_role_id'))
    user_technology_id = Column(Integer, ForeignKey('user_technologies.user_technology_id'))
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", backref="user_details")
    user_role = relationship("UserRole", backref="user_details")
    user_technology = relationship("UserTechnology", backref="user_details")


class Project(Base):
    __tablename__ = 'projects'

    project_id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255))
    project_description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey('users.id'))

    created_by = relationship("User", backref="projects")


class UserProject(Base):
    __tablename__ = 'user_projects'

    user_project_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    project_id = Column(Integer, ForeignKey('projects.project_id'))
    joined_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="user_projects")
    project = relationship("Project", backref="user_projects")


class TaskStatus(Base):
    __tablename__ = "task_status"
    task_status_id = Column(Integer, primary_key=True, index=True)
    task_status_name = Column(String)


class Task(Base):
    __tablename__ = 'tasks'

    task_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.project_id'))
    task_name = Column(String(255))
    task_description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status_id = Column(Integer, ForeignKey('task_status.task_status_id'))
    task_owner_id = Column(Integer, ForeignKey('users.id'))

    project = relationship("Project", backref="tasks")
    task_owner = relationship("User", foreign_keys=[task_owner_id])
