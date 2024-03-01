from fastapi import Depends, HTTPException, status, APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models.user import User
from models.task import TaskStatus, Task
from models.project import Project, UserProject
from routers.auth import  get_scope_user
from routers.logger import logger
from datetime import datetime
from schemas.task import TaskCreate, TaskStatusCreate, TaskDetail, TaskUpdate
from database.session import get_db

router = APIRouter(prefix="/tasks", tags=['tasks'])

templates = Jinja2Templates(directory="templates")

@router.get("/task/status/", response_class=HTMLResponse)
def render_task_status_template(request: Request):
    """
        Renders template for adding task status.
    """
    logger.info("Rendering template for adding task status")
    return templates.TemplateResponse("task_status.html", context={"request": request})

@router.post("/task_status/", response_class=HTMLResponse)
def create_task_status(request: Request, task_status: str = Form(...), db: Session = Depends(get_db)):
    """
        Creates a new task status.

        Args:
            task_status(str): Status of task.
            db (Session): Database session.

        Returns:
            Home page template response.

    """

    new_task_status = TaskStatus(**task_status.model_dump())
    db.add(new_task_status)
    db.commit()
    db.refresh(new_task_status)
    return RedirectResponse(url="/users/home/")


@router.get("/task/{user_id}/", response_class=HTMLResponse)
def render_task_template(request: Request, user_id: int, db: Session = Depends(get_db)):
    """
        Renders template for adding task for specific user.

        Args:
            user_id(int): ID of the user to create task for.
    """
    user = db.query(User).filter(User.id == user_id).first()
    logger.info("Rendering template for adding task")
    return templates.TemplateResponse("add_task.html", context={"request": request, "user_id": user_id, "user": user})

@router.post("/task/{user_id}/", response_class=HTMLResponse)
def create_task(request: Request, user_id: int, task_name: str = Form(...), task_description: str = Form(...),
        task_status: str = Form(...), db: Session = Depends(get_db), current_user: User = Depends(get_scope_user)):
    """
        Creates a new task with the provided details.

        Args:
            user_id (int): ID of the user to create task for.
            user_id(int): ID of the user to which task belongs.
            task_name(str): Name of the task.
            task_description(str): Description of the task.
            task_status(str): Status of the task.
            db (Session): Database session.

        Returns:
            Home page template response with success response.

        Raises:
            HTTPException: If project, user, or status not found.

    """
    if current_user != user_id:
        logger.error(
            f"User {current_user.username} attempted to create task for user ID {user_id}")
        raise HTTPException(status_code=403, detail="Forbidden: You can only create tasks for your own user ID")
    logger.info("Creating a new task")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    project = db.query(UserProject).filter(UserProject.user_id == user_id).first()
    if not project:
        logger.error(f"Project with user ID {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    task_status = TaskStatus(task_status_name=task_status)
    db.add(task_status)
    db.commit()
    db.refresh(task_status)
    new_task = Task(
        project_id=project.user_project_id,
        task_name=task_name,
        task_description=task_description,
        task_owner_id=user_id,
        status_id=task_status.task_status_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    logger.info("Task created successfully")
    user = db.query(User).filter(User.id == user_id).first()
    return templates.TemplateResponse("home.html", context={"request": request, "message":"Task created successfully", "user": user, "user_id":user_id})

@router.get("/details/{user_id}/{task_id}/", response_class=HTMLResponse)
def get_task_details(request: Request, user_id: int, task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_scope_user)):
    """
        Retrives task details for specific task.

        Args:
            task_id(int): ID of the task to get details for.
            user_id(int): ID of the user to which task belongs.
            db (Session): Database session.

        Returns:
            Task Details template response.

        Raises:
            HTTPException: If task with the specified id does not exist.

    """
    if current_user.id != user_id:
        logger.error(
            f"User {current_user.username} attempted to create task for user ID {user_id}")
        raise HTTPException(status_code=403, detail="Forbidden: You can only create tasks for your own user ID")
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
    user = db.query(User).filter(User.id == user_id).first()
    logger.info(f"Task details retrieved successfully for task with ID {task_id}")
    return templates.TemplateResponse("task_detail.html", context={"request":request, "task_detail":task_detail, "user_id": user_id, "user": user})

@router.get("/user/projects/{user_id}/projects/tasks/{project_id}/", response_class=HTMLResponse)
def get_tasks_for_project(request: Request, user_id: int, project_id: int, db: Session = Depends(get_db),current_user: User = Depends(get_scope_user) ):
    """
        Retrieves all tasks associated with a specific user and project.

        Args:
            user_id(int): ID of the user to get tasks for.
            project_id(int): ID of the project to get tasks for.

        Returns:
            Template response for listing tasks.

        Raises:
            HTTPException: If the project or user with the specified ID is not found.

    """
    if current_user.id != user_id:
        logger.error(
            f"User {current_user.username} attempted to create task for user ID {user_id}")
        raise HTTPException(status_code=403, detail="Forbidden: You can only create tasks for your own user ID")
    logger.info(f"Retrieving tasks for project with ID {project_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if project is None:
        logger.error(f"Project with ID {project_id} not found")
        raise HTTPException(status_code=404, detail="Project not found")
    tasks = project.tasks
    for task in tasks:
        status_name = db.query(TaskStatus.task_status_name).filter(TaskStatus.task_status_id == task.status_id).scalar()
        if not status_name:
            logger.error(f"Task status with id {task.status_id} does not exist")
        task.status_name = status_name
    logger.info(f"Tasks retrieved successfully for project with ID {project_id}")
    return templates.TemplateResponse("list_tasks.html", context={"request": request, "tasks":tasks})


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



@router.get("/task/{task_id}/project_detail/", response_class=HTMLResponse)
def get_task_with_project_details(request: Request, task_id: int, db: Session = Depends(get_db)):
    """
        Retrieves details of the task identified by the given task ID.

        Returns:
            Task details template response.

        Note:
            If the task with the specified ID is not found, returns None.
    """
    logger.info(f"Retrieving details for task with ID {task_id} along with project details")
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if task:
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
    else:
        logger.error(f"Task with ID {task_id} not found")
    return templates.TemplateResponse("task_detail.html", context={"request":request, "task_detail":task_project_details})

@router.get("/user/{user_id}/", response_class=HTMLResponse)
def get_tasks_for_user(request: Request, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_scope_user)):
    """
        Retrieves all tasks of user.

        Args:
            user_id(int): ID of the user to which task belongs.
            db (Session): Database session.

        Returns:
            Task list template response.

        Raises:
            HTTPException: If user not found.
    """
    if current_user.id != user_id:
        logger.error(
            f"User {current_user.username} attempted to create task for user ID {user_id}")
        raise HTTPException(status_code=403, detail="Forbidden: You can only create tasks for your own user ID")
    logger.info(f"Retrieving tasks for user with ID {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_project_ids = db.query(UserProject.project_id).filter(UserProject.user_id == user_id).all()
    project_ids = [project_id for project_id, in user_project_ids]
    projects = db.query(Project).filter(Project.project_id.in_(project_ids)).all()
    # tasks_list = []
    tasks = []
    for project in projects:
        tasks = project.tasks
        # tasks_list.append(tasks)
        for task in tasks:
            status_name = db.query(TaskStatus.task_status_name).filter(TaskStatus.task_status_id == task.status_id).scalar()
            if not status_name:
                logger.error(f"Task status with id {task.status_id} does not exist")
            task.status_name = status_name
    logger.info(f"Tasks retrieved successfully for user with ID {user_id}")
    return templates.TemplateResponse("list_tasks.html", context={"request": request, "tasks":tasks, "user_id":user_id, "user": user})

@router.get("/{user_id}/{task_id}/", response_class=HTMLResponse)
def render_task_update_template(request: Request, user_id: int, task_id:int, db: Session = Depends(get_db), current_user: User = Depends(get_scope_user)):
    """
        Renders template for updating task for specific user.

        Args:
            user_id(int): ID of the user to create task for.
    """
    if current_user.id != user_id:
        logger.error(
            f"User {current_user.username} attempted to create task for user ID {user_id}")
        raise HTTPException(status_code=403, detail="Forbidden: You can only create tasks for your own user ID")
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        logger.warning(f"Task with ID {task_id} not found")
        return None
    task_status = db.query(TaskStatus.task_status_name).filter(TaskStatus.task_status_id == task.status_id).scalar()
    user = db.query(User).filter(User.id == user_id).first()
    logger.info("Rendering template for updating task")
    return templates.TemplateResponse("edit_task.html", context={"request": request, "user_id": user_id, "user": user, "task":task,
    "task_status":task_status})

@router.put("/{user_id}/{task_id}/", response_class=HTMLResponse)
def update_task(request: Request, user_id:int, task_id: int, task_name: str = Form(...), task_description: str = Form(...),
        task_status: str = Form(...), db: Session = Depends(get_db), current_user:User = Depends(get_scope_user)):
    """
        Updates task with the provided details.

        Args:
            user_id (int): ID of the user to create task for.
            task_id(int): ID of the task to update.
            task_name(str): Name of the task.
            task_description(str): Description of the task.
            task_status(str): Status of the task.
            db (Session): Database session.

        Returns:
            Home page template response with success response.

        Raises:
            HTTPException: If task or user not found.

    """
    if current_user.id != user_id:
        logger.error(
            f"User {current_user.username} attempted to create task for user ID {user_id}")
        raise HTTPException(status_code=403, detail="Forbidden: You can only create tasks for your own user ID")
    logger.info(f"Updating a task with ID : {task_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db_task = db.query(Task).filter(Task.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_status = TaskStatus(task_status_name=task_status)
    db.add(task_status)
    db.commit()
    db.refresh(task_status)
    task_dict = dict()
    task_dict["task_name"] = task_name
    task_dict["task_description"] = task_description
    task_dict["status_id"] = task_status.task_status_id
    for attr, value in task_dict.items():
        setattr(db_task, attr, value)
    db.commit()
    db.refresh(db_task)

    logger.info("Task updated successfully")
    return templates.TemplateResponse("list_tasks.html", context={"request": request, "message":"Task updated successfully", "user": user, "user_id": user_id})

@router.get("/home/{user_id}/", response_class=HTMLResponse)
def render_edit_success_template(request: Request, user_id: int, db: Session = Depends(get_db), current_user:User = Depends(get_scope_user)):
    """
    Renders home page after successful edit operation.

    Args:
        user_id(int): ID of the user to which task belongs.

    Returns:
        Home page template response with success response.

    Raises:
        HTTPException: If user not found.
    """
    if current_user.id != user_id:
        logger.error(
            f"User {current_user.username} attempted to create task for user ID {user_id}")
        raise HTTPException(status_code=403, detail="Forbidden: You can only create tasks for your own user ID")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logger.info(f"Rendering template for home page")
    return templates.TemplateResponse("home.html", context={"request":request, "message":"Task updated successfully", "user": user, "user_id": user_id})

@router.get("/delete/{user_id}/{task_id}/", response_class=HTMLResponse)
def delete_task(request: Request, user_id: int, task_id: int, db: Session = Depends(get_db), current_user:User = Depends(get_scope_user)):
    """
    Delete the task with the specified task ID.

    Args:
        user_id: ID of the user to which task belongs.
        task_id: ID of the task to delete.
        db (Session): Database session.

    Returns:
        Home page template response with success response.

    Raises:
        HTTPException: If task or user not found.
    """
    if current_user.id != user_id:
        logger.error(
            f"User {current_user.username} attempted to create task for user ID {user_id}")
        raise HTTPException(status_code=403, detail="Forbidden: You can only create tasks for your own user ID")
    logger.info(f"Deleting a task with ID : {task_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db_task = db.query(Task).filter(Task.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return templates.TemplateResponse("home.html", context={"request": request, "message":"Task deleted successfully", "user": user, "user_id": user_id})
