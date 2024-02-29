from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models.project import Project, UserProject
from models.user import User
from routers.auth import get_scope_user
from schemas.project import ProjectCreate, ProjectResponse, UserProjectCreate
from routers.logger import logger
from database.session import get_db
from datetime import datetime

router = APIRouter(prefix="/projects", tags=['projects'])


templates = Jinja2Templates(directory="templates")

@router.get("/project/", response_class=HTMLResponse)
def render_project_template(request: Request):
    """
        Renders add project template.
    """
    logger.info("Rendering add project template")
    return templates.TemplateResponse("project.html", {"request": request})

@router.post("/projects/", response_class=HTMLResponse)
def create_project(request: Request, project_name: str = Form(...), project_description: str = Form(...),  db: Session = Depends(get_db)):
    """
        Creates a new project with the provided details.

        Args:
            project_name(str): Name of the project to create.
            project_description(str): Description of project.
            db (Session): Database session.

        Returns:
            Home page template response with success response.

    """
    logger.info("Creating a new project")
    new_project = Project(project_name=project_name, project_description=project_description, created_by_id=1)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    logger.info("New project created successfully")
    return RedirectResponse(url="/users/home/")


@router.get("/projects/user/{user_id}/", response_class=HTMLResponse)
def get_projects_created_by_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    """
        Retrieves all projects created by the user with the specified user ID.

        Args:
            user_id(int): ID of the user to list projects for.
            db (Session): Database session.

        Returns:
            Project list template response.

        Raises:
            HTTPException: If user with specified id does not exist.

    """
    logger.info(f"Retrieving projects created by user with ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    projects = db.query(Project).filter(Project.created_by_id == user_id).all()
    logger.info("Projects retrieved successfully")
    return templates.TemplateResponse("list_projects.html", {"request": request, "projects":projects})

@router.get("/user/project/{user_id}/", response_class=HTMLResponse)
def render_assign_project_template(request: Request, user_id: int, db: Session = Depends(get_db)):
    """
        Renders template for project assignment.

        Args:
            user_id(int): ID of the user to assign project to.
            db (Session): Database session.

        Returns:
            Template for assigning project.

        Raises:
            HTTPException: If user with specified id does not exist.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    projects = db.query(Project).all()
    logger.info("Rendering assign project template")
    return templates.TemplateResponse("assign_project.html", context={"request":request, "projects":projects, "user_id": user_id})


@router.post("/user_projects/{user_id}/", response_class=HTMLResponse)
def create_user_project(request: Request, user_id: int, project_id: int = Form(...), db: Session = Depends(get_db)):
    """
    Creates a new user project relationship.

    Args:
        user_id(int): ID of the user to create project for.
        project_id(int): ID of the project to assign.
        db (Session): Database session.

    Returns:
        Home page template response with success response.

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
    return RedirectResponse(url="/users/home/")

@router.get("/user_projects/{user_id}/projects/", response_class=HTMLResponse)
def get_user_projects(request: Request, user_id: int, db: Session = Depends(get_db)):
    """
        Retrieves projects associated with a specific user.

        Args:
            user_id (int): ID of the user.
            db (Session): Database session.

        Returns:
            List projects of specific user.

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
