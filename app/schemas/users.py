from pydantic import BaseModel, EmailStr, Field, ConfigDict
from .constants import (
    USERNAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    EMAIL_MIN_LENGTH,
    PASSWORD_MIN_LENGTH,
    USERNAME_MIN_LENGTH,
)


class BaseUserSchema(BaseModel):
    email: EmailStr = Field(
        min_length=EMAIL_MIN_LENGTH,
        max_length=EMAIL_MAX_LENGTH,
        description="Enter your email.",
    )
    user_name: str = Field(
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH,
        description="Enter your name.",
    )


class CreateUserSchema(BaseUserSchema):
    password: str = Field(
        min_length=PASSWORD_MIN_LENGTH, description="Enter your password"
    )


class UpdateUserSchema(BaseModel):
    email: EmailStr | None = Field(
        default=None, min_length=EMAIL_MIN_LENGTH, max_length=EMAIL_MAX_LENGTH
    )
    user_name: str | None = Field(
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH,
        default=None,
        description="Enter your name",
    )


class UserResponseSchema(BaseUserSchema):
    id: int
    model_config = ConfigDict(from_attributes=True)
