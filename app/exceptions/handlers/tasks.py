from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from app.exceptions.units.tasks_exceptions import (
    TaskForbiddenError,
    TaskNotFoundError,
    TaskInvalidDataError,
    TaskAlreadyExistsError,
)


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(TaskNotFoundError)
    def task_not_found_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Task not found or inactive"},
        )

    @app.exception_handler(TaskForbiddenError)
    def task_forbidden_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Only project owner can change task"},
        )

    @app.exception_handler(TaskAlreadyExistsError)
    def task_existing_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Task already exists"},
        )

    @app.exception_handler(TaskInvalidDataError)
    def task_invalid_data_handler(request, exc: TaskInvalidDataError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": {"field": exc.field, "reason": exc.reason}},
        )
