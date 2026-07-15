from sqlalchemy.exc import IntegrityError

from app.repositories.tasks import TaskRepository
from app.repositories.projects import ProjectRepository
from app.models.tasks import Task as TaskModel
from app.repositories.users import UserRepository
from app.schemas.tasks import TaskCreateSchema
from app.exceptions.units.tasks_exceptions import (
    TaskForbiddenError,
    TaskNotFoundError,
    TaskInvalidDataError,
    TaskAlreadyExistsError,
)
from app.exceptions.units.projects_exceptions import (
    ProjectNotFoundError,
    ProjectNotOwnerError,
)
from app.exceptions.units.users_exceptions import UserNotFoundError


class TaskService:
    def __init__(
        self,
        task_repository: TaskRepository,
        user_repo: UserRepository,
        project_repo: ProjectRepository,
    ):
        self.task_repo = task_repository
        self.user_repo = user_repo
        self.project_repo = project_repo

    async def get_task_by_id(
        self,
        task_id: int,
    ) -> TaskModel:

        task = await self.task_repo.select_one(task_id=task_id)
        if task is None:
            raise TaskNotFoundError()

        active_project = await self.project_repo.select_one(project_id=task.project_id)
        if active_project is None:
            raise ProjectNotFoundError()

        return task

    async def create_task(self, task_data: TaskCreateSchema, user_id: int) -> TaskModel:

        existing_project = await self.project_repo.select_one(
            project_id=task_data.project_id
        )
        if existing_project is None:
            raise ProjectNotFoundError()

        if existing_project.owner_id != user_id:
            raise TaskForbiddenError(action="create", status="project owner")

        if task_data.worker_id is not None:
            worker_filter = self.user_repo._buid_and_filter(user_id=task_data.worker_id)
            worker = await self.user_repo.get_user_on_filters(worker_filter)
            if worker is None:
                raise UserNotFoundError()

        task_data = task_data.model_dump()
        try:
            task = await self.task_repo.create(task_data)
            if task is None:
                await self.task_repo.db.rollback()
                raise TaskAlreadyExistsError()
            await self.task_repo.db.commit()
        except IntegrityError:
            await self.task_repo.db.rollback()
            raise

        return task
