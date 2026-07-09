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
