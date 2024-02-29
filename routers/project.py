from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.project import Project, UserProject
from models.user import User
from routers.auth import get_scope_user
from schemas.project import ProjectCreate, ProjectResponse, UserProjectCreate
from logger import logger
from database.session import get_db
from datetime import datetime

router = APIRouter(prefix="/projects", tags=['projects'])


@router.post("/projects/")
def create_project(project: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_scope_user)):
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


@router.get("/projects/user/{user_id}")
def get_projects_created_by_user(user_id: int, db: Session = Depends(get_db),  current_user: User = Depends(get_scope_user)):
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


@router.post("/user_projects/")
def create_user_project(user_project: UserProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_scope_user)):
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


@router.get("/user_projects/{user_id}/projects")
def get_user_projects(user_id: int, db: Session = Depends(get_db),  current_user: User = Depends(get_scope_user)):
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
