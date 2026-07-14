from pydantic import BaseModel, Field, ConfigDict
from app.models.tasks import TaskStatus
from datetime import datetime
from .constants import TITLE_MAX_LENGTH, TITLE_MIN_LENGTH, DESCRIPTION_MAX_LENGTH


class TaskBaseSchema(BaseModel):
    title: str = Field(
        ...,
        min_length=TITLE_MIN_LENGTH,
        max_length=TITLE_MAX_LENGTH,
        description="Task title",
    )
    project_id: int = Field(ge=1, description="Project id")

    model_config = ConfigDict(from_attributes=True)


class TaskShortResponseSchema(TaskBaseSchema):
    id: int
    created_at: datetime


class TaskResponseSchema(TaskShortResponseSchema):
    description: str | None = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH, description="Task description"
    )
    task_status: TaskStatus
    worker_id: int | None
    updated_at: datetime | None
    finished_at: datetime | None


class TaskCreateSchema(TaskBaseSchema):
    description: str | None = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH, description="Task description"
    )
    worker_id: int | None = Field(
        default=None,
        ge=1,
    )


class TaskUpdateSchema(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=TITLE_MIN_LENGTH,
        max_length=TITLE_MAX_LENGTH,
        description="Task title",
    )
    description: str | None = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH, description="Task description"
    )
    worker_id: int | None = Field(
        default=None,
        ge=1,
    )

    task_status: TaskStatus | None = None
