from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.exeptions.units.projects_exeptions import ProjectNotFoundError, ProjectNameExistingError


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(ProjectNameExistingError)
    def name_existing_handler(request: Request, exc):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content="Project name already existing."
        )

    @app.exception_handler(ProjectNotFoundError)
    def project_not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Project not found or inactive."
        )
