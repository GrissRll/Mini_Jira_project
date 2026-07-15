from sqlalchemy import select,UnaryExpression
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tasks import Task as TaskModel
from typing import List, Sequence, Any, Mapping
from app.types.ordering import Ordering
from app.types.filters import TasksFilter
from app.types.paginations import Pagination


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def build_ordering(ordering: Ordering) -> Sequence[UnaryExpression[Any]]:
        order_column: dict = {
            "id": TaskModel.id,
            "title": TaskModel.title,
            "task_status": TaskModel.task_status,
            "created_at": TaskModel.created_at,
        }

        if ordering.direction == "desc":
            ordered_list = [order_column[column].desc() for column in ordering.columns]
        else:
            ordered_list = [order_column[column].asc() for column in ordering.columns]
        if "id" not in ordering.columns:
            if ordering.direction == "desc":
                ordered_list.append(order_column["id"].desc())
            else:
                ordered_list.append(order_column["id"].asc())

        return ordered_list

    @staticmethod
    def build_filters(task_filter: TasksFilter) -> List[ColumnElement]:
        filters = [TaskModel.is_active == True]
        if task_filter.task_id is not None:
            filters.append(TaskModel.id == task_filter.task_id)
        if task_filter.project_id is not None:
            filters.append(TaskModel.project_id == task_filter.project_id)
        if task_filter.title is not None:
            filters.append(TaskModel.title == task_filter.title)
        if task_filter.worker_id is not None:
            filters.append(TaskModel.worker_id == task_filter.worker_id)
        if task_filter.task_status is not None:
            filters.append(TaskModel.task_status == task_filter.task_status)

        return filters

    async def select_one(self, task_filter: TasksFilter) -> TaskModel | None:
        filters = self.build_filters(task_filter)
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
