from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from models.user import User
from models.task import TaskStatus, Task
from models.project import Project
from routers.logger import logger
from datetime import datetime
from schemas.task import TaskCreate, TaskStatusCreate, TaskDetail
from database.session import get_db

router = APIRouter(prefix="/tasks", tags=['tasks'])


@router.post("/task_statuses/")
def create_task_status(task_status: TaskStatusCreate, db: Session = Depends(get_db)):
    """
    Creates a new task status.

    """
    new_task_status = TaskStatus(**task_status.dict())
    db.add(new_task_status)
    db.commit()
    db.refresh(new_task_status)
    return new_task_status


@router.post("/tasks/")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
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
    logger.info("Creating a new task")
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
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    logger.info("Task created successfully")
    return new_task

@router.get("/tasks/{task_id}", response_model=TaskDetail)
def get_task_details(task_id: int, db: Session = Depends(get_db)):
    """
    Creates a new task associated with a project, specifying the task name, description, owner, and status.

    """
    logger.info(f"Retrieving details for task with ID {task_id}")
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

@router.get("/projects/{project_id}/tasks/")
def get_tasks_for_project(project_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all tasks associated with a specific project identified by the given project ID.

    Raises:
        HTTPException: If the project with the specified ID is not found.

    """
    logger.info(f"Retrieving tasks for project with ID {project_id}")
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if project is None:
        logger.error(f"Project with ID {project_id} not found")
        raise HTTPException(status_code=404, detail="Project not found")
    tasks = project.tasks
    logger.info(f"Tasks retrieved successfully for project with ID {project_id}")
    return tasks


@router.get("/task/{task_id}/owner/")
def get_task_with_owner_details(task_id: int, db: Session = Depends(get_db)):
    """
    Retrieves details of the task identified by the given task ID including the owner's username and email.

    Returns:
        dict: Details of the task including task ID, name, description, owner's username, and email.

    Note:
        If the task with the specified ID is not found, returns None.

    """
    logger.info(f"Retrieving details for task with ID {task_id}")
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        logger.warning(f"Task with ID {task_id} not found")
        return None
    task_owner = task.task_owner
    owner_username = task_owner.username
    owner_email = task_owner.email

    task_details = {
        "task_id": task.task_id,
        "task_name": task.task_name,
        "task_description": task.task_description,
        "task_owner_username": owner_username,
        "task_owner_email": owner_email
    }
    logger.info(f"Details retrieved successfully for task with ID {task_id}")
    return task_details


@router.get("/task/{task_id}/project_detail/")
def get_task_with_project_details(task_id: int, db: Session = Depends(get_db)):
    """
    Retrieves details of the task identified by the given task ID along with details of the project it belongs to.

    Returns:
        dict: Details of the task including task ID, name, description, project ID, project name, and project description.

    Note:
        If the task with the specified ID is not found, returns None.
    """
    logger.info(f"Retrieving details for task with ID {task_id} along with project details")
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        logger.warning(f"Task with ID {task_id} not found")
        return None

    project = task.project

    task_project_details = {
        "task_id": task.task_id,
        "task_name": task.task_name,
        "task_description": task.task_description,
        "project_id": project.project_id,
        "project_name": project.project_name,
        "project_description": project.project_description,
    }
    logger.info(f"Details retrieved successfully for task with ID {task_id} along with project details")
    return task_project_details
