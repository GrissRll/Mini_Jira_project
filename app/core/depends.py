from .database import async_session_maker
from typing import AsyncGenerator
from app.repositories.users import UserRepository
from app.repositories.projects import ProjectRepository
from app.repositories.tasks import TaskRepository
from app.services.projects_service import ProjectService
from app.services.users_services import UserService
from app.services.tasks_service import TaskService
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.types.ordering import Ordering, TaskTypeOfOrdering, TaskOrderedColumns
from app.types.filters import TasksFilter
from app.models.tasks import TaskStatus
from app.schemas.constants import TITLE_MIN_LENGTH, TITLE_MAX_LENGTH
from app.types.paginations import Pagination
from app.models.users import User as UserModel
from app.core.auth import oauth2_scheme
from app.core.config import ALGORITHM, SECRET_KEY
import jwt


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async generator for session object"""
    async with async_session_maker() as session:
        yield session


async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


async def get_user_service(user_repo: UserRepository = Depends(get_user_repository)):
    return UserService(user_repository=user_repo)


async def get_project_repository(
    db: AsyncSession = Depends(get_db),
) -> ProjectRepository:
    return ProjectRepository(db)


async def get_project_service(
    project_repo: ProjectRepository = Depends(get_project_repository),
) -> ProjectService:
    return ProjectService(project_repository=project_repo)


async def get_task_repository(db: AsyncSession = Depends(get_db)):
    return TaskRepository(db=db)


async def get_task_service(
    task_repository: TaskRepository = Depends(get_task_repository),
    project_repository: ProjectRepository = Depends(get_project_repository),
    user_repository: UserRepository = Depends(get_user_repository),
):
    return TaskService(
        task_repository=task_repository,
        user_repo=user_repository,
        project_repo=project_repository,
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticated": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credential_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credential_exception
    result = await db.scalars(
        select(UserModel).where(UserModel.email == email, UserModel.is_active == True)
    )
    user = result.first()
    if user is None:
        raise credential_exception
    return user


def get_pagination(
    page_num: int = Query(default=1, ge=1, le=9999),
    page_size: int = Query(default=10, ge=1, le=99),
) -> Pagination:
    return Pagination(page_num=page_num, page_size=page_size)


def get_filters(
    task_id: int | None = Query(default=None, ge=1, le=1000000),
    project_id: int | None = Query(default=None, ge=1, le=100000),
    title: str | None = Query(
        default=None, min_length=TITLE_MIN_LENGTH, max_length=TITLE_MAX_LENGTH
    ),
    worker_id: int | None = Query(default=None, ge=1, le=100000),
    task_status: TaskStatus | None = Query(default=None),
) -> TasksFilter:
    return TasksFilter(
        task_id=task_id,
        task_status=task_status,
        title=title,
        worker_id=worker_id,
        project_id=project_id,
    )


def get_order(
    direction: TaskTypeOfOrdering = Query(default="asc"),
    columns: tuple[TaskOrderedColumns, ...] = Query(default=("id",)),
) -> Ordering:
    return Ordering(columns=columns, direction=direction)
