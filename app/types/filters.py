from dataclasses import dataclass
from app.models.tasks import TaskStatus


@dataclass(slots=True)
class TasksFilter:
    project_id: int | None = None
    title: str | None = None
    worker_id: int | None = None
    task_status: TaskStatus | None = None
