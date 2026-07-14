from app.repositories.tasks import TaskRepository


class TaskService:
    def __init__(self, task_repository: TaskRepository):
        self.task_repo = task_repository
