from sqlalchemy.orm import Session
from models.user import User
from models.task import Task, TaskStatus
from models.project import Project
from schemas.task import TaskCreate, TaskStatusCreate, TaskDetail
from database.session import get_db_session, commit_db
from logger import logger
from datetime import datetime
from fastapi import HTTPException


def create_task_status(task_status: TaskStatusCreate, db: Session = None):
    """
    Creates a new task status.

    """
    db = get_db_session(db)
    new_task_status = TaskStatus(**task_status.dict())
    new_task_status = commit_db(db, new_task_status)
    return new_task_status


def create_task(task: TaskCreate, db: Session = None, current_user: User = None):
    """
    Creates a new task with the provided details.

    Args:
        task (TaskCreate): Data model for creating a task.
        db (Session): Database session.

    Returns:
        Task: Newly created task.

    Raises:
        HTTPException: If project, user, or status not found.

    """
    db = get_db_session(db)
    project = db.query(Project).filter(Project.project_id == task.project_id).first()
    if not project:
        logger.error(f"Project with ID {task.project_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    user = db.query(User).filter(User.id == task.task_owner_id).first()
    if not user:
        logger.error(f"User with ID {task.task_owner_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    status = db.query(TaskStatus).filter(TaskStatus.task_status_id == task.task_status_id).first()
    if not status:
        logger.error(f"Task status with ID {task.task_status_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task status not found")
    new_task = Task(
        project_id=task.project_id,
        task_name=task.task_name,
        task_description=task.task_description,
        task_owner_id=task.task_owner_id,
        status_id=task.task_status_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    new_task = commit_db(db, new_task)

    logger.info("Task created successfully")
    return new_task


def get_task_details(task_id: int, db: Session = None):
    """
    Retrieves details for the task identified by the given task ID.

    """
    db = get_db_session(db)
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        logger.error(f"Task with ID {task_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    status_name = db.query(TaskStatus.task_status_name).filter(TaskStatus.task_status_id == task.status_id).scalar()
    project = db.query(Project.project_name, Project.project_description).filter(Project.project_id == task.project_id).first()

    task_detail = TaskDetail(
        task_id=task.task_id,
        task_name=task.task_name,
        task_description=task.task_description,
        project_name=project.project_name,
        project_description=project.project_description,
        status_name=status_name
    )

    logger.info(f"Task details retrieved successfully for task with ID {task_id}")
    return task_detail
