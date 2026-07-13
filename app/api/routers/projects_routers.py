from fastapi import APIRouter, Depends, status
from app.models.projects import Project as ProjectModel
from app.schemas.projects import (
    ProjectShortResponseSchema,
    UpdateProjectSchema,
    CreateProjectSchema,
    ResponseProjectSchema,
)
from app.schemas.responses import MessageResponse
from app.core.depends import get_project_service, get_current_user
from app.services.projects_service import ProjectService

from typing import List

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectShortResponseSchema], status_code=200)
async def get_projects(service: ProjectService = Depends(get_project_service)):
    return await service.get_projects()


@router.get("/{project_id}", response_model=ResponseProjectSchema, status_code=200)
async def get_project_by_id(
    project_id: int, service: ProjectService = Depends(get_project_service)
):
    return await service.get_project(project_id)


@router.get(
    "/owner/{owner_id}",
    response_model=List[ProjectShortResponseSchema],
    status_code=200,
)
async def get_owner_projects(
    owner_id: int, service: ProjectService = Depends(get_project_service)
):
    return await service.get_owner_projects(owner_id)
