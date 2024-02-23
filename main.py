from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from utils import hash_password, verify_password
from models import UserDetails, User, UserRole, UserTechnology, Project, UserProject, TaskStatus, Task, Base


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


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
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
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
def create_user(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
    db_user = User(username=username, email=email)
    db_user.password_hash = hash_password(password)  # You would need to implement hash_password function
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return templates.TemplateResponse("login.html", {"request": request, "username": username})

@app.post("/users/login")
def login_user(request: Request, email: str =  Form(...),password: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_email_and_password(email, password, db)
    return templates.TemplateResponse("home.html", {"request": request, "username": username})

@app.get("/roles/", response_class=HTMLResponse)
def render_role_template(request: Request):
    return templates.TemplateResponse("role.html", {"request": request})

@app.post("/user_roles/", response_class=HTMLResponse)
def create_user_role(request: Request, role_name: str = Form(...), db: Session = Depends(get_db)):
    new_user_role = UserRole(role_name=role_name)
    db.add(new_user_role)
    db.commit()
    db.refresh(new_user_role)
    return templates.TemplateResponse("home.html", {"request": request, "message": "Role added successfully"})

@app.get("/technology/", response_class=HTMLResponse)
def render_technology_template(request: Request):
    return templates.TemplateResponse("technology.html", {"request": request})

@app.post("/user_technologies/", response_class=HTMLResponse)
def create_user_technology(technology_name: str = Form(...), db: Session = Depends(get_db)):
    # new_user_technology = UserTechnology(**user_technology.dict())
    db.add(technology_name)
    db.commit()
    db.refresh(new_user_technology)
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/user_details/")
def create_user_details(user_details: UserDetailsCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_details.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_role = db.query(UserRole).filter(UserRole.user_role_id == user_details.user_role_id).first()
    if not user_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User role not found")
    user_technology = db.query(UserTechnology).filter(UserTechnology.user_technology_id == user_details.user_technology_id).first()
    if not user_technology:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User technology not found")
    new_user_detail = UserDetails(**user_details.dict())

    db.add(new_user_detail)
    db.commit()
    db.refresh(new_user_detail)

    return new_user_detail

@app.get("/users/", response_class=HTMLResponse)
def get_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("list_users.html", {"request": request, "users":users})


@app.get("/user_details/{user_id}", response_model=UserDetailResponse)
def get_user_details(request: Request, user_id: int, db: Session = Depends(get_db)):
    user_detail = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
    if not user_detail:
        raise HTTPException(status_code=404, detail="User details not found")
    user_role = db.query(UserRole).filter(UserRole.user_role_id == user_detail.user_role_id).first()
    user_technology = db.query(UserTechnology).filter(UserTechnology.user_technology_id == user_detail.user_technology_id).first()
    # return {
    #     "id": user_detail.id,
    #     "created_at": user_detail.created_at,
    #     "role_name": user_role.role_name,
    #     "technology_name": user_technology.technology_name
    # }
    return templates.TemplateResponse("user_details.html", {"request": request, "user":user_detail})

@app.get("/project/")
def render_project_template(request: Request):
    return templates.TemplateResponse("project.html", {"request": request})

@app.post("/projects/")
def create_project(request: Request, project_name: str = Form(...), project_description: str = Form(...),  db: Session = Depends(get_db)):
    # user = db.query(User).filter(User.id == project.created_by_id).first()
    # if not user:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    new_project = Project(project_name=project_name, project_description=project_description)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/projects/user/{user_id}", response_class=HTMLResponse)
def get_projects_created_by_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    projects = db.query(Project).filter(Project.created_by_id == user_id).all()
    return templates.TemplateResponse("list_projects.html", {"request": request, "projects":projects})


@app.get("/user/project/{user_id}/", response_class=HTMLResponse)
def render_assign_project_template(request: Request, user_id: int, db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return templates.TemplateResponse("assign_project.html", context={"request":request, "projects":projects, "user_id": user_id})

@app.post("/user_projects/{user_id}/", response_class=HTMLResponse)
def create_user_project(request: Request, user_id: int, project_id: int = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    new_user_project = UserProject(
        user_id=user_id,
        project_id=project_id,
        joined_at=datetime.utcnow()
    )
    db.add(new_user_project)
    db.commit()
    db.refresh(new_user_project)
    return templates.TemplateResponse("home.html", context={"request":request})


@app.get("/user_projects/{user_id}", response_class=HTMLResponse)
def get_user_projects(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
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

    return templates.TemplateResponse("list_user_projects.html", context={"request": request, "projects":project_responses})

@app.get("/task/status/")
def render_task_status_template(request: Request):
    return templates.TemplateResponse("task_status.html", context={"request": request})

@app.post("/task_statuses/")
def create_task_status(request: Request, task_status: str = Form(...), db: Session = Depends(get_db)):
    # new_task_status = TaskStatus(**task_status.dict())
    db.add(task_status)
    db.commit()
    db.refresh(new_task_status)
    return templates.TemplateResponse("home.html", context={"request": request})

@app.get("/task/")
def render_task_template(request: Request):
    return templates.TemplateResponse("add_task.html", context={"request": request})

@app.post("/tasks/")
def create_task(request: Request, name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.project_id == task.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    user = db.query(User).filter(User.id == task.task_owner_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    status = db.query(TaskStatus).filter(TaskStatus.task_status_id == task.task_status_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
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

    return templates.TemplateResponse("home.html", context={"request": request})


@app.get("/tasks/{task_id}", response_class=HTMLResponse)
def get_task_details(request: Request, task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
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
    return templates.TemplateResponse("task_detail.html", context={"request":request, "task_detail":task_detail})


@app.get("/logout/")
def logout(request: Request):
    return templates.TemplateResponse("login.html", context={"request":request})
