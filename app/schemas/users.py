from pydantic import BaseModel, EmailStr, Field


class BaseUserSchema(BaseModel):
    email: EmailStr = Field(min_length=10, description="Enter your email.")
    user_name: str = Field(min_length=3,max_length=40, description="Enter your name.")

class CreateUserSchema(BaseUserSchema):
    hashed_password:str = Field(min_length=10,description="Enter your password")

class UpdateUserSchema(BaseModel):
    email: EmailStr | None = None
    user_name: str | None = Field(min_length=3,
                                  max_length=40,
                                  default=None,
                                  description="Enter your name")

class UserResponseSchema(BaseUserSchema):
    id: int
    model_config = {"from_attributes": True}



