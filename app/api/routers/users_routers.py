from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.util import await_only

from app.models.users import User as UserModel
from app.core.depends import get_db, get_user_service
from app.schemas.users import UserResponseSchema, CreateUserSchema, UpdateUserSchema
from app.services.users_services import UserService
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/", status_code=200, response_model=List[UserResponseSchema])
async def get_all_users(service: UserService = Depends(get_user_service),
                        page_num: int = 1,
                        page_size: int = 10):
    """
        Get paginated users list.
        Return list of users.
    """

    return await service.get_all_users(page_num, page_size)


@router.post("/", status_code=201, response_model=UserResponseSchema)
async def create_new_user(user: CreateUserSchema, service: UserService = Depends(get_user_service)):
    """
        Create new user.
        Return created user.
    """
    return await service.create_user(user)


@router.get("/{user_id}", status_code=200, response_model=UserResponseSchema)
async def get_user_by_id(user_id: int, service: UserService = Depends(get_user_service)):
    """
        Get user by identifier.
        Return user.
    """
    return await service.get_user_by_id(user_id)


@router.patch("/users/{user_id}", response_model=UserResponseSchema, status_code=204)
async def update_user(user_id: int, user: UserModel, update_data: UpdateUserSchema,
                      service: UserService = Depends(get_user_service)):
    return await service.update_user(update_data, user, user_id)


@router.patch("/users/change_status/{user_id}", response_model=JSONResponse, status_code=204)
async def soft_delete(user_id: int, user: UserModel, service: UserService = Depends(get_user_service)):
    return await service.soft_delete(user, user_id)


@router.delete("/users/{user_id}", response_model=JSONResponse, status_code=204)
async def hard_delete(user_id: int, user: UserModel, service: UserService = Depends(get_user_service)):
    return await service.hard_delete(user, user_id)
