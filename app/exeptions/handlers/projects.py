from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.exeptions.units.projects_exeptions import (
    ProjectNotFoundError,
    ProjectNameExistingError,
    ProjectNotOwnerError,
    ProjectNameNotNullError,
)


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(ProjectNameExistingError)
    def name_existing_handler(request: Request, exc):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Project name already existing."},
        )

    @app.exception_handler(ProjectNotFoundError)
    def project_not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Project not found or inactive."},
        )

    @app.exception_handler(ProjectNameNotNullError)
    def project_name_null_handler(request: Request, exc):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Project name can't be null."},
        )

    @app.exception_handler(ProjectNotOwnerError)
    def not_project_owner_handler(request: Request, exc):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Only owner can update project."},
        )
