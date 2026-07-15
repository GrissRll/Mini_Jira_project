from sqlalchemy import select, Sequence as AlchemySequence, UnaryExpression
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tasks import Task as TaskModel, TaskStatus
from typing import List, Literal, Sequence, Any

OrderedColumns = Literal["id", "title", "task_status", "created_at"]
TypeOfOrdering = Literal["asc", "desc"]


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def build_ordering(
        columns: Sequence[OrderedColumns], ordering: TypeOfOrdering = "asc"
    ) -> Sequence[UnaryExpression[Any]]:
        order_column: dict = {
            "id": TaskModel.id,
            "title": TaskModel.title,
            "task_status": TaskModel.task_status,
            "created_at": TaskModel.created_at,
        }

        if ordering == "desc":
            ordered_list = [order_column[column].desc() for column in columns]
        else:
            ordered_list = [order_column[column].asc() for column in columns]
        if "id" not in columns:
            if ordering == "desc":
                ordered_list.append(order_column["id"].desc())
            else:
                ordered_list.append(order_column["id"].asc())

        return ordered_list

    @staticmethod
    def build_filters(
        task_id: int | None = None,
        project_id: int | None = None,
        title: str | None = None,
        worker_id: int | None = None,
        task_status: TaskStatus | None = None,
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
        if task_status is not None:
            filters.append(TaskModel.task_status == task_status)

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
