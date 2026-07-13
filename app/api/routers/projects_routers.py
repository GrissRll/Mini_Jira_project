from fastapi import APIRouter, Depends, status
from sqlalchemy.util import await_only

from app.models.projects import Project as ProjectModel
from app.models.users import User as UserModel
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


@router.post("/", response_model=ResponseProjectSchema, status_code=201)
async def create_project(
    project_data: CreateProjectSchema,
    service: ProjectService = Depends(get_project_service),
    user: UserModel = Depends(get_current_user),
):
    return await service.create_project(project_data=project_data, user=user)


@router.patch("/{project_id}", response_model=ResponseProjectSchema, status_code=200)
async def update_project(
    updated_data: UpdateProjectSchema,
    project_id: int,
    service: ProjectService = Depends(get_project_service),
    user: UserModel = Depends(get_current_user),
):
    return await service.update_project(
        updated_data=updated_data, user=user, project_id=project_id
    )


@router.patch(
    "/change_status/{project_id}", response_model=MessageResponse, status_code=200
)
async def soft_delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
    user: UserModel = Depends(get_current_user),
):
    return await service.soft_delete(project_id=project_id, user_id=user.id)
