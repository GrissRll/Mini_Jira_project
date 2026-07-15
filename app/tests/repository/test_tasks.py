import pytest
from sqlalchemy import func, select

from app.models.tasks import Task as TaskModel
from app.repositories.tasks import TaskRepository
from app.tests.data.tasks import (
    task_data_first,
    task_data_inactive,
    task_data_second,
)
from app.types.filters import TasksFilter
from app.types.ordering import Ordering
from app.types.paginations import Pagination


@pytest.mark.asyncio
async def test_select_one_by_id(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        repository = TaskRepository(session)

        task = await repository.select_one(task_filter=TasksFilter(task_id=1))

        assert task is not None
        assert task.id == 1
        assert task.title == task_data_first["title"]


@pytest.mark.asyncio
async def test_select_one_by_project_id(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        repository = TaskRepository(session)

        task = await repository.select_one(task_filter=TasksFilter(project_id=1))

        assert task is not None
        assert task.project_id == 1


@pytest.mark.asyncio
async def test_select_one_by_title(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        repository = TaskRepository(session)

        task = await repository.select_one(
            task_filter=TasksFilter(title=task_data_second["title"])
        )

        assert task is not None
        assert task.title == task_data_second["title"]


@pytest.mark.asyncio
async def test_select_one_by_worker_id(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        repository = TaskRepository(session)

        task = await repository.select_one(task_filter=TasksFilter(worker_id=2))

        assert task is not None
        assert task.worker_id == 2
        assert task.title == task_data_second["title"]


@pytest.mark.asyncio
async def test_select_one_by_combined_filters(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        repository = TaskRepository(session)

        task = await repository.select_one(
            task_filter=TasksFilter(
                project_id=1,
                title=task_data_first["title"],
                worker_id=1,
            )
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

        task = await repository.select_one(task_filter=TasksFilter(task_id=999))

        assert task is None


@pytest.mark.asyncio
async def test_select_one_skips_inactive_task(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        repository = TaskRepository(session)

        task = await repository.select_one(
            task_filter=TasksFilter(title=task_data_inactive["title"])
        )

        assert task is None


@pytest.mark.asyncio
async def test_create_task(async_session_maker, create_users_with_project):
    async with async_session_maker() as session:
        repository = TaskRepository(session)
        task_data = {
            "title": "Repository created task",
            "description": "Created in repository test",
            "project_id": 1,
            "worker_id": 2,
        }

        task = await repository.create(task_data)
        await session.commit()

        assert task is not None
        assert task.id is not None
        assert task.title == task_data["title"]
        assert task.description == task_data["description"]
        assert task.project_id == task_data["project_id"]
        assert task.worker_id == task_data["worker_id"]

        stored_task = await session.get(TaskModel, task.id)
        assert stored_task is not None
        assert stored_task.title == task_data["title"]


@pytest.mark.asyncio
async def test_create_returns_none_for_duplicate_project_title(
    async_session_maker,
    create_users_with_project,
):
    async with async_session_maker() as session:
        repository = TaskRepository(session)
        task_data = {
            "title": "Duplicate repository task",
            "project_id": 1,
        }

        first_task = await repository.create(task_data)
        await session.commit()
        duplicate_task = await repository.create(task_data)

        assert first_task is not None
        assert duplicate_task is None
        tasks_count = await session.scalar(
            select(func.count(TaskModel.id)).where(
                TaskModel.project_id == 1,
                TaskModel.title == task_data["title"],
            )
        )
        assert tasks_count == 1


@pytest.mark.asyncio
async def test_select_many_returns_only_active_tasks(
    async_session_maker, create_tasks
):
    async with async_session_maker() as session:
        repository = TaskRepository(session)

        tasks = await repository.select_many(
            order=Ordering(columns=("id",)),
            pagination=Pagination(),
            task_filter=TasksFilter(),
        )

        assert [task["id"] for task in tasks] == [1, 2]
        assert task_data_inactive["title"] not in {
            task["title"] for task in tasks
        }


@pytest.mark.asyncio
async def test_select_many_applies_filters(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        repository = TaskRepository(session)

        tasks = await repository.select_many(
            order=Ordering(columns=("id",)),
            pagination=Pagination(),
            task_filter=TasksFilter(
                project_id=1,
                worker_id=2,
                title=task_data_second["title"],
            ),
        )

        assert len(tasks) == 1
        assert tasks[0]["id"] == 2
        assert tasks[0]["title"] == task_data_second["title"]


@pytest.mark.asyncio
async def test_select_many_applies_descending_order(
    async_session_maker, create_tasks
):
    async with async_session_maker() as session:
        repository = TaskRepository(session)

        tasks = await repository.select_many(
            order=Ordering(columns=("id",), direction="desc"),
            pagination=Pagination(),
            task_filter=TasksFilter(),
        )

        assert [task["id"] for task in tasks] == [2, 1]


@pytest.mark.asyncio
async def test_select_many_applies_pagination(async_session_maker, create_tasks):
    async with async_session_maker() as session:
        repository = TaskRepository(session)

        tasks = await repository.select_many(
            order=Ordering(columns=("id",)),
            pagination=Pagination(page_num=2, page_size=1),
            task_filter=TasksFilter(),
        )

        assert len(tasks) == 1
        assert tasks[0]["id"] == 2
