import pytest

from app.exceptions.units.projects_exceptions import ProjectNotFoundError
from app.exceptions.units.tasks_exceptions import TaskNotFoundError
from app.models.projects import Project as ProjectModel
from app.repositories.projects import ProjectRepository
from app.repositories.tasks import TaskRepository
from app.repositories.users import UserRepository
from app.services.tasks_service import TaskService
from app.tests.data.tasks import task_data_first


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

        task = await service.get_task_by_id(task_id=1)

        assert task.id == 1
        assert task.title == task_data_first["title"]
        assert task.project_id == task_data_first["project_id"]


@pytest.mark.asyncio
async def test_get_task_by_id_not_found(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        service = build_task_service(session)

        with pytest.raises(TaskNotFoundError):
            await service.get_task_by_id(task_id=999)


@pytest.mark.asyncio
async def test_get_task_by_id_inactive_task(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        service = build_task_service(session)

        with pytest.raises(TaskNotFoundError):
            await service.get_task_by_id(task_id=3)


@pytest.mark.asyncio
async def test_get_task_by_id_inactive_project(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        project = await session.get(ProjectModel, 1)
        assert project is not None
        project.is_active = False
        await session.commit()

        service = build_task_service(session)

        with pytest.raises(ProjectNotFoundError):
            await service.get_task_by_id(task_id=1)
