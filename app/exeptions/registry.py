from app.exeptions.handlers.users import register_exception_handler as users_handlers
from app.exeptions.handlers.projects import register_exception_handlers as project_handlers
from fastapi import FastAPI


def register_handlers(app:FastAPI):
    users_handlers(app)
    project_handlers(app)

