from fastapi import Depends, HTTPException, status, APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.user import UserDetail, UserRole, UserTechnology, User
from database.session import get_db
from routers.logger import logger
from schemas.user import UserCreate, GetUser
from schemas.user_role import UserRoleCreate
from schemas.user_detail import UserDetailResponse, UserDetailsCreate
from schemas.user_technology import UserTechnologyCreate
from utils.hash_pwd import hash_password
from utils.verify_pwd import verify_password
from services.user import get_details_of_user, create_user, create_user_technology_data, create_user_role_data, create_details_of_user
from routers.auth import get_scope_user
router = APIRouter(prefix="/users", tags=['users'])

templates = Jinja2Templates(directory="templates")


def get_user_by_email_and_password(email: str, password: str, db: Session):

    """
        Retrieves a user by email and password from the database session

        Args:
            email: Email of current user.
            password: Password of current user.
            db (Session): Database session.

        Returns:
            user object.

    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        logger.warning("Failed login attempt for given email")
        raise HTTPException(status_code=404, detail="User not found or invalid credentials")
    return user


@router.get("/home/", response_class=HTMLResponse)
def home(request: Request, current_user: User = Depends(get_scope_user) ):
    """
    Renders home page template response.

    Returns:
        Home page template response
    """
    logger.info("Rendering home page template")
    return templates.TemplateResponse(name="home.html", context={"request":request, "user":current_user})

@router.get("/register/", response_class=HTMLResponse)
def render_register_template(request: Request):
    """
    Renders registration template.

    Returns:
        Registration template response
    """
    logger.info("Renders user registration template")
    return templates.TemplateResponse(name="register.html", context={"request":request}
    )


@router.post("/register/", response_class=HTMLResponse)
def register_user(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...), is_admin_user: bool= Form(False),
    db: Session = Depends(get_db)):
    """
    Creates a new user with the provided user details in the database.

    Args:
        username(str): Username of current user.
        password(str): Password of current user.
        email(str): Email of current user.
        db (Session): Database session.

    Returns:
        Login template response.
    """
    # TODO this code is same as in user.py. If we don't need to use this API, remove this code.
    # create_user_model = User(
    #     username=create_user_request.username,
    #     email=create_user_request.email,
    #     password_hash=bcrypt_context.hash(create_user_request.password_hash)
    # )
    # db.add(create_user_model)
    # db.commit()
    # db.refresh(create_user_model)
    # return {
    #     "email": create_user_model.email,
    #     "username": create_user_model.username
    # }
    user = db.query(User).filter(or_(User.username == username, User.email == email)).first()
    if user:
        logger.error(f"User with the provided details already exists {username} {email}")
        return RedirectResponse(url='/users/register/')
    logger.info("Creating a new user with username: %s and email: %s", username, email)
    user = create_user(username, password, email, is_admin_user, db)
    return RedirectResponse(url='/users/login/')

@router.get("/login/", response_class=HTMLResponse)
def login_user(request: Request, response_class=HTMLResponse):
    """
    Renders login template.

    Returns:
        Login template response
    """
    logger.info("Renders user login template")
    return templates.TemplateResponse(name="login.html", context={"request":request}
    )

@router.post("/users/login/", response_class=HTMLResponse)
def login_user(request: Request, email: str =  Form(...),password: str = Form(...), db: Session = Depends(get_db)):
    """
    Logs in user with email and password.

    Args:
        password(str): Password of current user.
        email(str): Email of current user.
        db (Session): Database session.

    Returns:
        Home page template response.
    """
    user = get_user_by_email_and_password(email, password, db)
    return templates.TemplateResponse("home.html", {"request": request, "username": user.username, "message": "User Logged in successfully"})

@router.get("/users/", response_class=HTMLResponse)
def get_users(request: Request, db: Session = Depends(get_db)):
    """
    Retrieves list of all users.

    Returns:
        Users lists tenplate response.
    """
    users = db.query(User).all()
    logger.info("Rendering user list template response")
    return templates.TemplateResponse("list_users.html", {"request": request, "users":users})

@router.post("/user/details/{user_id}/", response_class=HTMLResponse)
def create_user_details(request: Request, user_id: int, user_role_id: str = Form(...), user_technology_id: str = Form(...), db: Session = Depends(get_db)):
    """
    Creates a new user detail entry with the provided user details in the database.

    Params:
        user_id: ID of the user.
        user_role_id: Role ID.
        user_technology_id: Technology ID.
        db (Session): Database session.

    Returns:
        User details template response

    Raises:
        HTTPException: If user, user role, or user technology not found.

    """
    print("dfdsfsdfsdfsdfsdf", user_role_id, user_technology_id)
    logger.info("Creating a new user detail entry with user_id: %d", user_id)
    user, user_detail  = create_details_of_user(user_id, user_role_id, user_technology_id, db)
    return templates.TemplateResponse("user_details.html", {"request": request, "user": user, "user_role":user_detail[1],
    "user_technology": user_detail[2],
    "roles": db.query(UserRole).order_by(UserRole.role_name).all(),
    "technologies": db.query(UserTechnology).order_by(UserTechnology.technology_name).all()})



@router.get("/user/details/{user_id}/", response_class=HTMLResponse)
def get_user_details(request: Request, user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves user details for the specified user ID.
    """
    # logger.info("Retrieving user details for user ID: %d", user_id)
    user, user_detail = get_details_of_user(user_id, db)
    if not user_detail:
        return templates.TemplateResponse("user_details.html", {"request": request, "user": user,
        "roles": db.query(UserRole).order_by(UserRole.role_name).all(),
        "technologies": db.query(UserTechnology).order_by(UserTechnology.technology_name).all()})
    else:
        return templates.TemplateResponse("user_details.html", {"request": request, "user": user, "user_role":user_detail[1],
        "user_technology": user_detail[2],
        "roles": db.query(UserRole).order_by(UserRole.role_name).all(),
        "technologies": db.query(UserTechnology).order_by(UserTechnology.technology_name).all()})


@router.get("/roles/", response_class=HTMLResponse)
def render_role_template(request: Request):
    """
    Renders template for adding role.

    Returns:
        Add role template response.
    """
    logger.info("Rendering template for adding role")
    return templates.TemplateResponse("role.html", {"request": request})

@router.post("/user/roles/", response_class=HTMLResponse)
def create_user_role(request: Request, role_name: str = Form(...), db: Session = Depends(get_db)):
    """
    Creates a new user role with the provided role details in the database.

    Args:
        role_name(str): Name of role.
        db (Session): Database session.

    Returns:
        Home page template with sucess response.
    """
    logger.info("Creating a new user role with name: %s", role_name)
    create_user_role_data(role_name, db)
    return RedirectResponse(url="/users/home/")


@router.get("/technology/", response_class=HTMLResponse)
def render_technology_template(request: Request):
    """
    Renders template for addind technology.

    Returns:
        Add technology template response.
    """
    logger.info("Rendering template for adding technology")
    return templates.TemplateResponse("technology.html", {"request": request})

@router.post("/user/technologies/", response_class=HTMLResponse)
def create_user_technology(request: Request, technology_name: str = Form(...), db: Session = Depends(get_db)):
    """
    Creates a new user technology with the provided technology details in the database.

    Args:
        technology_name(str): Name of the technology to create.
        db (Session): Database session.

    Returns:
        Home page template with success response.
    """
    logger.info("Creating a new user technology with name: %s", technology_name)
    create_user_technology_data(technology_name, db)
    return RedirectResponse(url="/users/home/")


@router.get("/logout/", response_class=HTMLResponse)
def logout(request: Request):
    """
    Logs out user.

    Returns:
        Login template with success response.
    """
    return templates.TemplateResponse("login.html", context={"request":request, "message":"User logged out successfully"})
