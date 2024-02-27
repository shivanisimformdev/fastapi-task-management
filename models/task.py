from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base
from datetime import datetime


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