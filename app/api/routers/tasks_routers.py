from fastapi import APIRouter, Depends, Path
from app.models.users import User as UserModel
from app.types.filters import TasksFilter
from app.schemas.tasks import (
    TaskShortResponseSchema,
    TaskCreateSchema,
    TaskUpdateSchema,
    TaskResponseSchema,
)
from app.schemas.responses import MessageResponse
from app.core.depends import (
    get_task_service,
    get_current_user,
    get_filters,
    get_pagination,
    get_order,
)
from app.services.tasks_service import TaskService

from typing import List

from app.types.ordering import Ordering
from app.types.paginations import Pagination

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}", response_model=TaskResponseSchema, status_code=200)
async def get_task_by_id(
    task_id: int = Path(ge=1),
    service: TaskService = Depends(get_task_service),
    user: UserModel = Depends(get_current_user),
):
    """
    Get task by identifier.
    Return task.
    """
    task_filter = TasksFilter(task_id=task_id)

    return await service.get_task_by_id(task_filter=task_filter)


@router.post("/", response_model=TaskResponseSchema, status_code=201)
async def create_task(
    task_data: TaskCreateSchema,
    service: TaskService = Depends(get_task_service),
    user: UserModel = Depends(get_current_user),
):
    """
    Create new task.
    Return created task.
    """
    return await service.create_task(task_data, user.id)


@router.get("/", response_model=List[TaskShortResponseSchema], status_code=200)
async def get_tasks(
    service: TaskService = Depends(get_task_service),
    user: UserModel = Depends(get_current_user),
    task_filter: TasksFilter = Depends(get_filters),
    pagination: Pagination = Depends(get_pagination),
    ordering: Ordering = Depends(get_order),
):
    """
    Get tasks using filters, ordering and pagination.
    Return list of tasks.
    """
    return await service.select_tasks(
        task_filter=task_filter, ordering=ordering, pagination=pagination
    )
