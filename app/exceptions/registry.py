from app.exceptions.handlers.users import register_exception_handler as users_handlers
from app.exceptions.handlers.projects import (
    register_exception_handlers as project_handlers,
)
from app.exceptions.handlers.tasks import (
    register_exception_handlers as task_handlers,
)
from fastapi import FastAPI


def register_handlers(app: FastAPI):
    users_handlers(app)
    project_handlers(app)
    task_handlers(app)
