from fastapi import APIRouter, Depends, Path
from app.models.users import User as UserModel
from app.schemas.tasks import (
    TaskShortResponseSchema,
    TaskCreateSchema,
    TaskUpdateSchema,
    TaskResponseSchema,
)
from app.schemas.responses import MessageResponse
from app.core.depends import get_task_service, get_current_user
from app.services.tasks_service import TaskService

from typing import List

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}", response_model=TaskResponseSchema, status_code=200)
async def get_task_by_id(
    task_id: int = Path(ge=1),
    service: TaskService = Depends(get_task_service),
    user: UserModel = Depends(get_current_user),
):
    return await service.get_task_by_id(task_id=task_id)


@router.post("/", response_model=TaskResponseSchema, status_code=201)
async def create_task(
    task_data: TaskCreateSchema,
    service: TaskService = Depends(get_task_service),
    user: UserModel = Depends(get_current_user),
):
    return await service.create_task(task_data, user.id)
