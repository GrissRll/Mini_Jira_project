from pydantic import BaseModel, Field, ConfigDict
from app.models.users import User as UserModel
from app.schemas.users import UserResponseSchema
from app.models.tasks import Task as TaskModel
from datetime import datetime
from .constants import DESCRIPTION_MAX_LENGTH, TITLE_MAX_LENGTH,TITLE_MIN_LENGTH


class BaseProjectSchema(BaseModel):
    pass


class CreateProjectSchema(BaseProjectSchema):
    title: str = Field(..., min_length=TITLE_MIN_LENGTH, max_length=TITLE_MAX_LENGTH, description="Field for project name.")
    description: str | None = Field(default=None, max_length=DESCRIPTION_MAX_LENGTH, description="Project description")


class ResponseProjectSchema(CreateProjectSchema):
    id: int
    # tasks: list[ResponseTaskSchema] = Field(default_factory=list, description="Tasks list for project")
    owner: UserResponseSchema = Field(description="Project owner")
    created_at: datetime = Field(description="Project created time")

    model_config = ConfigDict(from_attributes=True)


class UpdateProjectSchema(BaseProjectSchema):
    title: str | None = Field(default=None, min_length=TITLE_MIN_LENGTH, max_length=TITLE_MAX_LENGTH, description="Field for project name.")
    description: str | None = Field(default=None, max_length=DESCRIPTION_MAX_LENGTH, description="Project description")


class ProjectShortResponseSchema(BaseProjectSchema):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)
