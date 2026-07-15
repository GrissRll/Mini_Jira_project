from dataclasses import dataclass
from app.models.tasks import TaskStatus


@dataclass(slots=True)
class TasksFilter:
    task_id: int | None = None
    project_id: int | None = None
    title: str | None = None
    worker_id: int | None = None
    task_status: TaskStatus | None = None
