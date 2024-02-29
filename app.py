from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from routers import auth, project, task, user
from database.session import engine
from database.base import Base

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth.router)
app.include_router(project.router)
app.include_router(task.router)
app.include_router(user.router)
Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=engine)

@app.get("/")
def landing_page(request: Request):
    return templates.TemplateResponse("login.html", context={"request": request})

@app.on_event("startup")
def startup_event():
    return RedirectResponse(url="/")
