from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from utils import hash_password, verify_password
from models import UserDetails, User, UserRole, UserTechnology, Project, UserProject, TaskStatus, Task
from database import Base



app = FastAPI()


Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

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

@app.get("/home/")
def home(request: Request, response_class=HTMLResponse):
    return templates.TemplateResponse(name="home.html", context={"request":request})

@app.get("/register/")
def register_user(request: Request, response_class=HTMLResponse):
    return templates.TemplateResponse(name="register.html", context={"request":request}
    )

@app.post("/user/")
def create_user(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...),
    role_name : str = Form(...), technology_name : str = Form(...), db: Session = Depends(get_db)):
    """
        Creates a new user with the provided user details in the database.

    """
    logger.info("Creating a new user with username: %s and email: %s", username, email)
    db_user = User(username=username, email=email)
    db_user.password_hash = hash_password(password)  # You would need to implement hash_password function
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info("User created successfully with ID: %d", db_user.id)
    return templates.TemplateResponse("login.html", {"request": request, "username": username, "message":"User registered succsessfully"})


@app.post("/users/login")
def login_user(request: Request, email: str =  Form(...),password: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_email_and_password(email, password, db)
    return templates.TemplateResponse("home.html", {"request": request, "username": user.username, "message": "User Logged in successfully"})

@app.get("/roles/", response_class=HTMLResponse)
def render_role_template(request: Request):
    return templates.TemplateResponse("role.html", {"request": request})

@app.post("/user_roles/", response_class=HTMLResponse)
def create_user_role(request: Request, role_name: str = Form(...), db: Session = Depends(get_db)):
    """
    Creates a new user role with the provided role details in the database.

    """
    logger.info("Creating a new user role with name: %s", role_name)
    new_user_role = UserRole(role_name=role_name)
    db.add(new_user_role)
    db.commit()
    db.refresh(new_user_role)
    logger.info("User role created successfully with ID: %d", new_user_role.user_role_id)
    return templates.TemplateResponse("home.html", {"request": request, "message": "Role added successfully"})

@app.get("/technology/", response_class=HTMLResponse)
def render_technology_template(request: Request):
    return templates.TemplateResponse("technology.html", {"request": request})

@app.post("/user_technologies/", response_class=HTMLResponse)
def create_user_technology(request: Request, technology_name: str = Form(...), db: Session = Depends(get_db)):
    """
    Creates a new user technology with the provided technology details in the database.

    """
    logger.info("Creating a new user technology with name: %s", technology_name)
    new_user_technology = UserTechnology(technology_name=technology_name)
    db.add(new_user_technology)
    db.commit()
    db.refresh(new_user_technology)
    logger.info("User technology created successfully with ID: %d", new_user_technology.user_technology_id)
    return templates.TemplateResponse("home.html", {"request": request, "message": "Technology added successfully"})

@app.post("/user/details/{user_id}/", response_class=HTMLResponse)
def create_user_details(request: Request, user_id: int, user_role_id: str = Form(...), user_technology_id: str = Form(...), db: Session = Depends(get_db)):
    """
    Creates a new user detail entry with the provided user details in the database.

    Args:
        user_details (UserDetailsCreate): Details of the user to be created.

    Returns:
        UserDetails: Newly created user detail object.

    Raises:
        HTTPException: If user, user role, or user technology not found.

    """
    logger.info("Creating a new user detail entry with user_id: %d", user_id)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error("User not found with ID: %d", user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_role = db.query(UserRole).filter(UserRole.user_role_id == user_role_id).first()
    if not user_role:
        logger.error("User role not found with ID: %d", user_role_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User role not found")
    user_technology = db.query(UserTechnology).filter(UserTechnology.user_technology_id == user_technology_id).first()
    if not user_technology:
        logger.error("User technology not found with ID: %d", user_technology_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User technology not found")
    new_user_detail = UserDetails(user_id=user_id, user_role_id=user_role_id, user_technology_id=user_technology_id)

    db.add(new_user_detail)
    db.commit()
    db.refresh(new_user_detail)
    logger.info("User detail entry created successfully with ID: %d", new_user_detail.id)
    user_detail = db.query(UserDetails, UserRole.role_name, UserTechnology.technology_name).join(UserRole,
    UserDetails.user_role_id == UserRole.user_role_id).join(UserTechnology,
    UserDetails.user_technology_id == UserTechnology.user_technology_id).filter(UserDetails.user_id == user_id).first()
    return templates.TemplateResponse("user_details.html", {"request": request, "user": user, "user_role":user_detail[1],
    "user_technology": user_detail[2],
    "roles": db.query(UserRole).order_by(UserRole.role_name).all(),
    "technologies": db.query(UserTechnology).order_by(UserTechnology.technology_name).all()})

@app.get("/users/", response_class=HTMLResponse)
def get_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("list_users.html", {"request": request, "users":users})


@app.get("/user/details/{user_id}/", response_class=HTMLResponse)
def get_user_details(request: Request, user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves user details for the specified user ID.
    """
    # user_detail = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
    logger.info("Retrieving user details for user ID: %d", user_id)
    # user_detail = db.query(UserDetails).filter(User.id == user_id).first()
    # if not user_detail:
    #     logger.error("User details not found for user ID: %d", user_id)
    #     raise HTTPException(status_code=404, detail="User details not found")
    # user_role = db.query(UserRole).filter(UserRole.user_role_id == user_detail.user_role_id).first()
    # user_technology = db.query(UserTechnology).filter(UserTechnology.user_technology_id == user_detail.user_technology_id).first()
    # user_detail = {
    #     "id": user_detail.id,
    #     "role_name": user_role.role_name,
    #     "technology_name": user_technology.technology_name
    # }
    user = db.query(User).filter(User.id == user_id).first()
    user_detail = db.query(UserDetails, UserRole.role_name, UserTechnology.technology_name).join(UserRole,
    UserDetails.user_role_id == UserRole.user_role_id).join(UserTechnology,
    UserDetails.user_technology_id == UserTechnology.user_technology_id).filter(UserDetails.user_id == user_id).first()
    logger.info("User details retrieved successfully for user ID: %d", user_id)
    return templates.TemplateResponse("user_details.html", {"request": request, "user": user, "user_role":user_detail[1],
    "user_technology": user_detail[2],
    "roles": db.query(UserRole).order_by(UserRole.role_name).all(),
    "technologies": db.query(UserTechnology).order_by(UserTechnology.technology_name).all()})

@app.get("/project/", response_class=HTMLResponse)
def render_project_template(request: Request):
    return templates.TemplateResponse("project.html", {"request": request})

@app.post("/projects/", response_class=HTMLResponse)
def create_project(request: Request, project_name: str = Form(...), project_description: str = Form(...),  db: Session = Depends(get_db)):
    """
        Creates a new project with the provided details.

    """
    logger.info("Creating a new project")
    # user = db.query(User).filter(User.id == project.created_by_id).first()
    # if not user:
        # logger.error("User not found for creating project")
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    new_project = Project(project_name=project_name, project_description=project_description, created_by_id=1)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    logger.info("New project created successfully")
    return templates.TemplateResponse("home.html", {"request": request, "message":"Project added successfully"})


@app.get("/projects/user/{user_id}", response_class=HTMLResponse)
def get_projects_created_by_user(request: Request, user_id: int, db: Session = Depends(get_db)):
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
    return templates.TemplateResponse("list_projects.html", {"request": request, "projects":projects})


@app.get("/user/project/{user_id}/", response_class=HTMLResponse)
def render_assign_project_template(request: Request, user_id: int, db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return templates.TemplateResponse("assign_project.html", context={"request":request, "projects":projects, "user_id": user_id})

@app.post("/user_projects/{user_id}/", response_class=HTMLResponse)
def create_user_project(request: Request, user_id: int, project_id: int = Form(...), db: Session = Depends(get_db)):
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
    # user = db.query(User).filter(User.id == user_id).first()
    logger.info(f"Creating user project relationship for user ID: {user_id} and project ID: {project_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        logger.error(f"Project with ID {user_project.project_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    new_user_project = UserProject(
        user_id=user_id,
        project_id=project_id,
        joined_at=datetime.utcnow()
    )
    db.add(new_user_project)
    db.commit()
    db.refresh(new_user_project)
    logger.info("User project relationship created successfully")
    return templates.TemplateResponse("home.html", context={"request":request, "message":"Project assigned successfully"})


@app.get("/user_projects/{user_id}/projects", response_class=HTMLResponse)
def get_user_projects(request: Request, user_id: int, db: Session = Depends(get_db)):
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
            created_by_id=1
        )
        project_responses.append(project_response)

    logger.info(f"Projects retrieved successfully for user with ID: {user_id}")
    return templates.TemplateResponse("list_user_projects.html", context={"request": request, "projects":project_responses, "user_id": user_id})

@app.get("/task/status/")
def render_task_status_template(request: Request, response_class=HTMLResponse):
    return templates.TemplateResponse("task_status.html", context={"request": request})

@app.post("/task_statuses/")
def create_task_status(request: Request, task_status: str = Form(...), db: Session = Depends(get_db)):
    """
    Creates a new task status.

    """
    # new_task_status = TaskStatus(**task_status.dict())
    db.add(task_status)
    db.commit()
    db.refresh(new_task_status)
    return templates.TemplateResponse("home.html", context={"request": request})

@app.get("/user_projects/{user_id}/projects/task/{project_id}", response_class=HTMLResponse)
def render_task_template(request: Request, user_id: int, project_id: int):
    return templates.TemplateResponse("add_task.html", context={"request": request, "user_id": user_id, "project_id": project_id})

@app.post("/user_projects/{user_id}/projects/task/{project_id}", response_class=HTMLResponse)
def create_task(request: Request, user_id: int, project_id: int, task_name: str = Form(...), task_description: str = Form(...), db: Session = Depends(get_db)):
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
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        logger.error(f"Project with ID {project_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # status = db.query(TaskStatus).filter(TaskStatus.task_status_id == task.task_status_id).first()
    # if not status:
    #     logger.error(f"Task status with ID {task.task_status_id} not found")
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task status not found")
    new_task = Task(
        project_id=project_id,
        task_name=task_name,
        task_description=task_description,
        task_owner_id=user_id,
        # status_id=task.task_status_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    logger.info("Task created successfully")
    return templates.TemplateResponse("home.html", context={"request": request, "message":"Task added successfully"})


@app.get("/tasks/{task_id}", response_class=HTMLResponse)
def get_task_details(request: Request, task_id: int, db: Session = Depends(get_db)):
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
    return templates.TemplateResponse("task_detail.html", context={"request":request, "task_detail":task_detail})



@app.get("/user_projects/{user_id}/projects/tasks/{project_id}", response_class=HTMLResponse)
def get_tasks_for_project(request: Request, user_id: int, project_id: int, db: Session = Depends(get_db)):
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
    return templates.TemplateResponse("list_tasks.html", context={"request": request, "tasks":tasks})


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
    return templates.TemplateResponse("task_detail.html", context={"request":request, "task_detail":task_detail})


@app.get("/logout/", response_class=HTMLResponse)
def logout(request: Request):
    return templates.TemplateResponse("login.html", context={"request":request, "message":"User logged out successfully"})
