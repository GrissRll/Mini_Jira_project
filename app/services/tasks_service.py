from app.repositories.tasks import TaskRepository
from app.repositories.projects import ProjectRepository
from app.repositories.users import UserRepository


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
