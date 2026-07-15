import pytest
from sqlalchemy import select

from app.exceptions.units.projects_exceptions import ProjectNotFoundError
from app.exceptions.units.tasks_exceptions import (
    TaskAlreadyExistsError,
    TaskForbiddenError,
    TaskNotFoundError,
)
from app.exceptions.units.users_exceptions import UserNotFoundError
from app.models.projects import Project as ProjectModel
from app.models.tasks import Task as TaskModel
from app.models.users import User as UserModel
from app.repositories.projects import ProjectRepository
from app.repositories.tasks import TaskRepository
from app.repositories.users import UserRepository
from app.services.tasks_service import TaskService
from app.schemas.tasks import TaskCreateSchema
from app.tests.data.tasks import task_data_first, task_data_second
from app.types.filters import TasksFilter
from app.types.ordering import Ordering
from app.types.paginations import Pagination


def build_task_service(session) -> TaskService:
    return TaskService(
        task_repository=TaskRepository(session),
        user_repo=UserRepository(session),
        project_repo=ProjectRepository(session),
    )


@pytest.mark.asyncio
async def test_get_task_by_id(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        service = build_task_service(session)

        task = await service.get_task_by_id(task_filter=TasksFilter(task_id=1))

        assert task.id == 1
        assert task.title == task_data_first["title"]
        assert task.project_id == task_data_first["project_id"]


@pytest.mark.asyncio
async def test_get_task_by_id_not_found(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        service = build_task_service(session)

        with pytest.raises(TaskNotFoundError):
            await service.get_task_by_id(task_filter=TasksFilter(task_id=999))


@pytest.mark.asyncio
async def test_get_task_by_id_inactive_task(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        service = build_task_service(session)

        with pytest.raises(TaskNotFoundError):
            await service.get_task_by_id(task_filter=TasksFilter(task_id=3))


@pytest.mark.asyncio
async def test_get_task_by_id_inactive_project(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        project = await session.get(ProjectModel, 1)
        assert project is not None
        project.is_active = False
        await session.commit()

        service = build_task_service(session)

        with pytest.raises(ProjectNotFoundError):
            await service.get_task_by_id(task_filter=TasksFilter(task_id=1))


@pytest.mark.asyncio
async def test_select_tasks_returns_filtered_ordered_page(
    async_session_maker, create_tasks
):
    async with async_session_maker() as session:
        service = build_task_service(session)

        tasks = await service.select_tasks(
            task_filter=TasksFilter(project_id=1),
            ordering=Ordering(columns=("id",), direction="desc"),
            pagination=Pagination(page_num=1, page_size=1),
        )

        assert len(tasks) == 1
        assert tasks[0]["id"] == 2
        assert tasks[0]["title"] == task_data_second["title"]


@pytest.mark.asyncio
async def test_create_task(async_session_maker, create_users_with_project):
    async with async_session_maker() as session:
        service = build_task_service(session)
        task_data = TaskCreateSchema(
            title="Service created task",
            description="Created in service test",
            project_id=1,
            worker_id=2,
        )

        task = await service.create_task(task_data=task_data, user_id=1)

        assert task.id is not None
        assert task.title == task_data.title
        assert task.worker_id == task_data.worker_id
        stored_task = await session.scalar(
            select(TaskModel).where(TaskModel.id == task.id)
        )
        assert stored_task is not None


@pytest.mark.asyncio
async def test_create_task_without_worker(
    async_session_maker,
    create_users_with_project,
):
    async with async_session_maker() as session:
        service = build_task_service(session)
        task_data = TaskCreateSchema(
            title="Unassigned task",
            project_id=1,
        )

        task = await service.create_task(task_data=task_data, user_id=1)

        assert task.worker_id is None


@pytest.mark.asyncio
async def test_create_task_project_not_found(
    async_session_maker,
    create_users_with_project,
):
    async with async_session_maker() as session:
        service = build_task_service(session)
        task_data = TaskCreateSchema(title="Missing project", project_id=999)

        with pytest.raises(ProjectNotFoundError):
            await service.create_task(task_data=task_data, user_id=1)


@pytest.mark.asyncio
async def test_create_task_forbidden_for_non_owner(
    async_session_maker,
    create_users_with_project,
):
    async with async_session_maker() as session:
        service = build_task_service(session)
        task_data = TaskCreateSchema(title="Forbidden task", project_id=1)

        with pytest.raises(TaskForbiddenError) as exc_info:
            await service.create_task(task_data=task_data, user_id=2)

        assert exc_info.value.action == "create"
        assert exc_info.value.status == "project owner"


@pytest.mark.asyncio
async def test_create_task_worker_not_found(
    async_session_maker,
    create_users_with_project,
):
    async with async_session_maker() as session:
        service = build_task_service(session)
        task_data = TaskCreateSchema(
            title="Missing worker",
            project_id=1,
            worker_id=999,
        )

        with pytest.raises(UserNotFoundError):
            await service.create_task(task_data=task_data, user_id=1)


@pytest.mark.asyncio
async def test_create_task_inactive_worker_not_found(
    async_session_maker,
    create_users_with_project,
):
    async with async_session_maker() as session:
        worker = await session.get(UserModel, 2)
        assert worker is not None
        worker.is_active = False
        await session.commit()
        service = build_task_service(session)
        task_data = TaskCreateSchema(
            title="Inactive worker",
            project_id=1,
            worker_id=2,
        )

        with pytest.raises(UserNotFoundError):
            await service.create_task(task_data=task_data, user_id=1)


@pytest.mark.asyncio
async def test_create_task_duplicate_title(
    async_session_maker,
    create_users_with_project,
):
    async with async_session_maker() as session:
        service = build_task_service(session)
        task_data = TaskCreateSchema(title="Duplicate service task", project_id=1)
        await service.create_task(task_data=task_data, user_id=1)

        with pytest.raises(TaskAlreadyExistsError):
            await service.create_task(task_data=task_data, user_id=1)
