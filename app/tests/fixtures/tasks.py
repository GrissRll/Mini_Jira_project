import pytest

from app.models.tasks import Task as TaskModel
from app.tests.data.tasks import (
    task_data_first,
    task_data_inactive,
    task_data_second,
)


@pytest.fixture(scope="function")
async def create_tasks(async_session_maker, create_users_with_project):
    async with async_session_maker() as session:
        tasks = [
            TaskModel(**task_data_first),
            TaskModel(**task_data_second),
            TaskModel(**task_data_inactive),
        ]
        session.add_all(tasks)
        await session.commit()
