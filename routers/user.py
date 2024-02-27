from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from models.user import UserDetail, UserRole, UserTechnology, User

from database.session import get_db
from routers.logger import logger
from schemas.user import UserCreate, GetUser
from schemas.user_role import UserRoleCreate
from schemas.user_detail import UserDetailResponse, UserDetailsCreate
from schemas.user_technology import UserTechnologyCreate
from utils.hash_pwd import hash_password
from utils.verify_pwd import verify_password
from services.user import get_user_details, create_user, create_user_technology, create_user_role, create_user_details

router = APIRouter(prefix="/users", tags=['users'])


def get_user_by_email_and_password(email: str, password: str, db: Session):

    """
    Retrieves a user by email and password from the database session
    Returns: user object

    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        logger.warning("Failed login attempt for given email")
        raise HTTPException(status_code=404, detail="User not found or invalid credentials")
    return user


@app.get("/home/", response_class=HTMLResponse)
def home(request: Request, response_class=HTMLResponse):
    """
    Redirects to home page
    Returns: home page template response
    """
    return templates.TemplateResponse(name="home.html", context={"request":request})

@app.get("/register/", response_class=HTMLResponse)
def register_user(request: Request, response_class=HTMLResponse):
    """
    Renders registration template
    Returns: registration template response
    """
    return templates.TemplateResponse(name="register.html", context={"request":request}
    )

@app.post("/user/", response_class=HTMLResponse)
def create_user(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
    """
    Creates a new user with the provided user details in the database
    Returns: login template response
    """
    logger.info("Creating a new user with username: %s and email: %s", username, email)
    user = create_user(user, db)
    return templates.TemplateResponse("login.html", {"request": request, "username": user.username, "message":"User registered succsessfully"})

@app.post("/users/login", response_class=HTMLResponse)
def login_user(request: Request, email: str =  Form(...),password: str = Form(...), db: Session = Depends(get_db)):
    """
    Logs in user with email and password
    Returns: home page template response
    """
    user = get_user_by_email_and_password(email, password, db)
    return templates.TemplateResponse("home.html", {"request": request, "username": user.username, "message": "User Logged in successfully"})

@app.get("/users/", response_class=HTMLResponse)
def get_users(request: Request, db: Session = Depends(get_db)):
    """
    Retrives all users.
    Returns: home page template response
    """
    users = db.query(User).all()
    return templates.TemplateResponse("list_users.html", {"request": request, "users":users})

@app.post("/user/details/{user_id}/", response_class=HTMLResponse)
def create_user_details(request: Request, user_id: int, user_role_id: str = Form(...), user_technology_id: str = Form(...), db: Session = Depends(get_db)):
    """
    Creates a new user detail entry with the provided user details in the database.

    Params:
        user_id: id of the user
        user_role_id; role id of user
        user_technology_id: technology id of user

    Returns:
        user details template response

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



@app.get("/user/details/{user_id}/", response_class=HTMLResponse)
def get_user_details(request: Request, user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves user details for the specified user ID.
    """
    logger.info("Retrieving user details for user ID: %d", user_id)
    user = db.query(User).filter(User.id == user_id).first()
    user_detail = db.query(UserDetails, UserRole.role_name, UserTechnology.technology_name).join(UserRole,
    UserDetails.user_role_id == UserRole.user_role_id).join(UserTechnology,
    UserDetails.user_technology_id == UserTechnology.user_technology_id).filter(UserDetails.user_id == user_id).first()
    logger.info("User details retrieved successfully for user ID: %d", user_id)
    return templates.TemplateResponse("user_details.html", {"request": request, "user": user, "user_role":user_detail[1],
    "user_technology": user_detail[2],
    "roles": db.query(UserRole).order_by(UserRole.role_name).all(),
    "technologies": db.query(UserTechnology).order_by(UserTechnology.technology_name).all()})


@app.get("/roles/", response_class=HTMLResponse)
def render_role_template(request: Request):
    return templates.TemplateResponse("role.html", {"request": request})

@app.post("/user_roles/", response_class=HTMLResponse)
def create_user_role(request: Request, role_name: str = Form(...), db: Session = Depends(get_db)):
    """
    Creates a new user role with the provided role details in the database.

    """
    logger.info("Creating a new user role with name: %s", role_name)
    create_user_role(user_role, db)
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
    create_user_technology(user_technology, db)
    return templates.TemplateResponse("home.html", {"request": request, "message": "Technology added successfully"})


@app.get("/logout/", response_class=HTMLResponse)
def logout(request: Request):
    return templates.TemplateResponse("login.html", context={"request":request, "message":"User logged out successfully"})
