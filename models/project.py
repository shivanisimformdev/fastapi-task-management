from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base
from datetime import datetime


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