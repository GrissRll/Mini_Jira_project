from sqlalchemy import select, UnaryExpression
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
        """
        Build a list of SQLAlchemy ordering expressions for task queries.

        Return list of ordering expressions.
        """
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
        """
        Build a list of SQLAlchemy filter expressions for task queries.

        Return list of filter conditions.
        """
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
        """
        SELECT query for searching an active task by filters.

        Return task or None.
        """
        filters = self.build_filters(task_filter)
        stmt = select(TaskModel).where(*filters)
        task = await self.db.scalar(stmt)
        return task

    async def create(self, task_data: dict) -> TaskModel | None:
        """
        INSERT query for creating a new task.

        Return created task or None if it already exists.
        """
        stmt = (
            insert(TaskModel)
            .values(**task_data)
            .on_conflict_do_nothing(constraint="un_tasks_project_title")
            .returning(TaskModel)
        )
        result = await self.db.execute(stmt)
        task = result.scalar_one_or_none()
        return task

    async def select_many(
        self, order: Ordering, pagination: Pagination, task_filter: TasksFilter
    ) -> Sequence[Mapping[str, Any]]:
        """
        SELECT query for retrieving active tasks with query parameters.

        Return filtered, ordered and paginated sequence of tasks.
        """
        filters = self.build_filters(task_filter=task_filter)
        order_expression = self.build_ordering(ordering=order)

        stmt = (
            select(
                TaskModel.id,
                TaskModel.title,
                TaskModel.project_id,
                TaskModel.created_at,
            )
            .where(*filters)
            .order_by(*order_expression)
            .offset((pagination.page_num - 1) * pagination.page_size)
            .limit(pagination.page_size)
        )
        task = (await self.db.execute(stmt)).mappings().all()
        return task
