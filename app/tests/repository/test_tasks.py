import pytest

from app.repositories.tasks import TaskRepository
from app.tests.data.tasks import (
    task_data_first,
    task_data_inactive,
    task_data_second,
)


@pytest.mark.asyncio
async def test_select_one_by_id(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        repository = TaskRepository(session)

        task = await repository.select_one(task_id=1)

        assert task is not None
        assert task.id == 1
        assert task.title == task_data_first["title"]


@pytest.mark.asyncio
async def test_select_one_by_project_id(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        repository = TaskRepository(session)

        task = await repository.select_one(project_id=1)

        assert task is not None
        assert task.project_id == 1


@pytest.mark.asyncio
async def test_select_one_by_title(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        repository = TaskRepository(session)

        task = await repository.select_one(title=task_data_second["title"])

        assert task is not None
        assert task.title == task_data_second["title"]


@pytest.mark.asyncio
async def test_select_one_by_worker_id(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        repository = TaskRepository(session)

        task = await repository.select_one(worker_id=2)

        assert task is not None
        assert task.worker_id == 2
        assert task.title == task_data_second["title"]


@pytest.mark.asyncio
async def test_select_one_by_combined_filters(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        repository = TaskRepository(session)

        task = await repository.select_one(
            project_id=1,
            title=task_data_first["title"],
            worker_id=1,
        )

        assert task is not None
        assert task.project_id == 1
        assert task.title == task_data_first["title"]
        assert task.worker_id == 1


@pytest.mark.asyncio
async def test_select_one_returns_none_for_unknown_id(
    async_session_maker, create_tasks
):
    async with async_session_maker() as session:
        repository = TaskRepository(session)

        task = await repository.select_one(task_id=999)

        assert task is None


@pytest.mark.asyncio
async def test_select_one_skips_inactive_task(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        repository = TaskRepository(session)

        task = await repository.select_one(title=task_data_inactive["title"])

        assert task is None
