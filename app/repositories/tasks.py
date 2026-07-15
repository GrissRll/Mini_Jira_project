from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tasks import Task as TaskModel
from typing import List


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def build_filters(
        task_id: int | None = None,
        project_id: int | None = None,
        title: str | None = None,
        worker_id: int | None = None,
    ) -> List[ColumnElement]:
        filters = [TaskModel.is_active == True]
        if task_id is not None:
            filters.append(TaskModel.id == task_id)
        if project_id is not None:
            filters.append(TaskModel.project_id == project_id)
        if title is not None:
            filters.append(TaskModel.title == title)
        if worker_id is not None:
            filters.append(TaskModel.worker_id == worker_id)

        return filters

    async def select_one(
        self,
        task_id: int | None = None,
        project_id: int | None = None,
        title: str | None = None,
        worker_id: int | None = None,
    ) -> TaskModel | None:
        filters = self.build_filters(
            task_id=task_id, project_id=project_id, title=title, worker_id=worker_id
        )
        stmt = select(TaskModel).where(*filters)
        task = await self.db.scalar(stmt)
        return task

    async def create(self, task_data: dict) -> TaskModel | None:
        stmt = (
            insert(TaskModel)
            .values(**task_data)
            .on_conflict_do_nothing(constraint="un_tasks_project_title")
            .returning(TaskModel)
        )
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()
        return task
