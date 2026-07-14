from app.repositories.tasks import TaskRepository
from app.repositories.projects import ProjectRepository
from app.models.tasks import Task as TaskModel
from app.repositories.users import UserRepository
from app.exceptions.units.tasks_exceptions import (
    TaskForbiddenError,
    TaskNotFoundError,
    TaskInvalidDataError,
    TaskAlreadyExistsError,
)
from app.exceptions.units.projects_exceptions import ProjectNotFoundError


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
