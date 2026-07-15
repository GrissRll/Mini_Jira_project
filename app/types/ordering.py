from dataclasses import dataclass

from typing import Literal

TaskOrderedColumns = Literal["id", "title", "task_status", "created_at"]
TaskTypeOfOrdering = Literal["asc", "desc"]

@dataclass(slots=True)
class Ordering:
    columns: tuple[TaskOrderedColumns, ...]
    direction: TaskTypeOfOrdering = "asc"

