from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import auth, project, task, user
from database.session import engine
from database.base import Base
app = FastAPI()

# Include routers
app.include_router(auth.router)
app.include_router(project.router)
app.include_router(task.router)
app.include_router(user.router)

app.mount("/static", StaticFiles(directory="static"), name="static")
