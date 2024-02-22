from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from utils import hash_password, verify_password
from models import UserDetails, User, UserRole, UserTechnology, Project, UserProject, TaskStatus, Task
from database import Base
import logging



app = FastAPI()

Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserCreate(BaseModel):
    """
    Model for creating a new User.
    """
    username: str
    email: str
    password: str


class GetUser(BaseModel):
    """
    Model for getting user details.
    """
    email: str
    password: str


class UserRoleCreate(BaseModel):
    """
    Model for creating a new UserRole.
    """
    role_name: str


class UserTechnologyCreate(BaseModel):
    """
    Model for creating a new UserTechnology.
    """
    technology_name: str


class UserDetailsCreate(BaseModel):
    """
    Model for creating UserDetails.
    """
    user_id: int
    user_role_id: int
    user_technology_id: int


class UserDetailResponse(BaseModel):
    """
    Response model for UserDetail.
    """
    id: int
    created_at: datetime
    role_name: str
    technology_name: str


class ProjectCreate(BaseModel):
    """
    Model for creating a new Project.
    """
    project_name: str
    project_description: str
    created_by_id: int


class UserProjectCreate(BaseModel):
    """
    Model for creating a new UserProject.
    """
    user_id: int
    project_id: int


class ProjectResponse(BaseModel):
    """
    Response model for Project.
    """
    project_id: int
    project_name: str
    project_description: str
    created_at: datetime
    updated_at: datetime
    created_by_id: int


class TaskStatusCreate(BaseModel):
    """
    Model for creating a new TaskStatus.
    """
    task_status_name: str


class TaskCreate(BaseModel):
    """
    Model for creating a new Task.
    """
    project_id: int
    task_name: str
    task_description: str
    task_owner_id: int
    task_status_id: int


class TaskDetail(BaseModel):
    """
    Response model for TaskDetail.
    """
    task_id: int
    task_name: str
    task_description: str
    project_name: str
    project_description: str
    status_name: str


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


def get_user_by_email_and_password(email: str, password: str, db: Session):

    """
    Retrieves a user by email and password from the database session.
    Returns:
        User: Retrieved user object.

    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        logger.warning("Failed login attempt for given email")
        raise HTTPException(status_code=404, detail="User not found or invalid credentials")
    return user


@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
        Creates a new user with the provided user details in the database.

    """
    logger.info("Creating a new user with username: %s and email: %s", user.username, user.email)
    db_user = User(username=user.username, email=user.email)
    db_user.password_hash = hash_password(user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info("User created successfully with ID: %d", db_user.id)
    return db_user

@app.get("/users/login")
def login_user(user: GetUser, db: Session = Depends(get_db)):
    user = get_user_by_email_and_password(user.email, user.password, db)
    return user


@app.post("/user_roles/")
def create_user_role(user_role: UserRoleCreate, db: Session = Depends(get_db)):
    """
    Creates a new user role with the provided role details in the database.

    """
    logger.info("Creating a new user role with name: %s", user_role.role_name)
    new_user_role = UserRole(**user_role.dict())
    db.add(new_user_role)
    db.commit()
    db.refresh(new_user_role)
    logger.info("User role created successfully with ID: %d", new_user_role.user_role_id)
    return new_user_role

@app.post("/user_technologies/")
def create_user_technology(user_technology: UserTechnologyCreate, db: Session = Depends(get_db)):
    """
    Creates a new user technology with the provided technology details in the database.

    """
    logger.info("Creating a new user technology with name: %s", user_technology.technology_name)
    new_user_technology = UserTechnology(**user_technology.dict())
    db.add(new_user_technology)
    db.commit()
    db.refresh(new_user_technology)
    logger.info("User technology created successfully with ID: %d", new_user_technology.user_technology_id)
    return new_user_technology

@app.post("/user_details/")
def create_user_details(user_details: UserDetailsCreate, db: Session = Depends(get_db)):
    """
    Creates a new user detail entry with the provided user details in the database.

    Args:
        user_details (UserDetailsCreate): Details of the user to be created.

    Returns:
        UserDetails: Newly created user detail object.

    Raises:
        HTTPException: If user, user role, or user technology not found.

    """
    logger.info("Creating a new user detail entry with user_id: %d", user_details.user_id)
    user = db.query(User).filter(User.id == user_details.user_id).first()
    if not user:
        logger.error("User not found with ID: %d", user_details.user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_role = db.query(UserRole).filter(UserRole.user_role_id == user_details.user_role_id).first()
    if not user_role:
        logger.error("User role not found with ID: %d", user_details.user_role_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User role not found")
    user_technology = db.query(UserTechnology).filter(UserTechnology.user_technology_id == user_details.user_technology_id).first()
    if not user_technology:
        logger.error("User technology not found with ID: %d", user_details.user_technology_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User technology not found")
    new_user_detail = UserDetails(**user_details.dict())

    db.add(new_user_detail)
    db.commit()
    db.refresh(new_user_detail)

    logger.info("User detail entry created successfully with ID: %d", new_user_detail.id)
    return new_user_detail

@app.get("/user_details/{user_id}", response_model=UserDetailResponse)
def get_user_details(user_id: int, db: Session = Depends(get_db)):

    """
    Retrieves user details for the specified user ID.
    """

    # user_detail = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
    logger.info("Retrieving user details for user ID: %d", user_id)
    user_detail = db.query(UserDetails).get(user_id)

    if not user_detail:
        logger.error("User details not found for user ID: %d", user_id)
        raise HTTPException(status_code=404, detail="User details not found")
    user_role = db.query(UserRole).filter(UserRole.user_role_id == user_detail.user_role_id).first()
    user_technology = db.query(UserTechnology).filter(UserTechnology.user_technology_id == user_detail.user_technology_id).first()
    logger.info("User details retrieved successfully for user ID: %d", user_id)
    return {
        "id": user_detail.id,
        "created_at": user_detail.created_at,
        "role_name": user_role.role_name,
        "technology_name": user_technology.technology_name
    }


@app.post("/projects/")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """
        Creates a new project with the provided details.

    """
    logger.info("Creating a new project")
    user = db.query(User).filter(User.id == project.created_by_id).first()
    if not user:
        logger.error("User not found for creating project")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    new_project = Project(**project.dict())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    logger.info("New project created successfully")
    return new_project


@app.get("/projects/user/{user_id}")
def get_projects_created_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all projects created by the user with the specified user ID.

    """
    logger.info(f"Retrieving projects created by user with ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    projects = db.query(Project).filter(Project.created_by_id == user_id).all()
    logger.info("Projects retrieved successfully")
    return projects


@app.post("/user_projects/")
def create_user_project(user_project: UserProjectCreate, db: Session = Depends(get_db)):
    """
    Creates a new user project relationship.

    Args:
        user_project (UserProjectCreate): Data model for creating a user project relationship.
        db (Session): Database session.

    Returns:
        UserProject: Newly created user project relationship.

    Raises:
        HTTPException: If user or project not found.
    """
    # user = db.query(User).filter(User.id == user_project.user_id).first()
    logger.info(f"Creating user project relationship for user ID: {user_project.user_id} and project ID: {user_project.project_id}")
    user = db.query(User).get(user_project.user_id)
    if not user:
        logger.error(f"User with ID {user_project.user_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    project = db.query(Project).filter(Project.project_id == user_project.project_id).first()
    if not project:
        logger.error(f"Project with ID {user_project.project_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    new_user_project = UserProject(
        user_id=user_project.user_id,
        project_id=user_project.project_id,
        joined_at=datetime.utcnow()
    )
    db.add(new_user_project)
    db.commit()
    db.refresh(new_user_project)
    logger.info("User project relationship created successfully")
    return new_user_project


@app.get("/user_projects/{user_id}/projects")
def get_user_projects(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves projects associated with a specific user.

    Args:
        user_id (int): ID of the user.
        db (Session): Database session.

    Returns:
        List[ProjectResponse]: List of projects associated with the user.

    Raises:
        HTTPException: If user not found.

    """
    # user = db.query(User).filter(User.id == user_id).first()
    logger.info(f"Retrieving projects for user with ID: {user_id}")
    user = db.query(User).get(user_id)
    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_project_ids = db.query(UserProject.project_id).filter(UserProject.user_id == user_id).all()
    project_ids = [project_id for project_id, in user_project_ids]
    projects = db.query(Project).filter(Project.project_id.in_(project_ids)).all()

    project_responses = []
    for project in projects:
        project_response = ProjectResponse(
            project_id=project.project_id,
            project_name=project.project_name,
            project_description=project.project_description,
            created_at=project.created_at,
            updated_at=project.updated_at,
            created_by_id=project.created_by_id
        )
        project_responses.append(project_response)

    logger.info(f"Projects retrieved successfully for user with ID: {user_id}")
    return project_responses


@app.post("/task_statuses/")
def create_task_status(task_status: TaskStatusCreate, db: Session = Depends(get_db)):
    """
    Creates a new task status.

    """
    new_task_status = TaskStatus(**task_status.dict())
    db.add(new_task_status)
    db.commit()
    db.refresh(new_task_status)
    return new_task_status


@app.post("/tasks/")
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

@app.get("/tasks/{task_id}", response_model=TaskDetail)
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

@app.get("/projects/{project_id}/tasks/")
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


@app.get("/task/{task_id}/owner/")
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


@app.get("/task/{task_id}/project_detail/")
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
