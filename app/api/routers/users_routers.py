from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.users import User as UserModel
from app.schemas.users import UserResponseSchema, CreateUserSchema, UpdateUserSchema
from app.schemas.responses import MessageResponse
from app.core.depends import get_user_service, get_current_user
from app.services.users_services import UserService

from typing import List

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", status_code=200, response_model=List[UserResponseSchema])
async def get_all_users(
    service: UserService = Depends(get_user_service),
    page_num: int = 1,
    page_size: int = 10,
):
    """
    Get paginated users list.
    Return list of users.
    """

    return await service.get_all_users(page_num, page_size)


@router.post("/", status_code=201, response_model=UserResponseSchema)
async def create_new_user(
    user: CreateUserSchema, service: UserService = Depends(get_user_service)
):
    """
    Create new user.
    Return created user.
    """
    return await service.create_user(user)


@router.get("/{user_id}", status_code=200, response_model=UserResponseSchema)
async def get_user_by_id(
    user_id: int, service: UserService = Depends(get_user_service)
):
    """
    Get user by identifier.
    Return user.
    """
    return await service.get_user_by_id(user_id)


@router.patch("/{user_id}", response_model=UserResponseSchema, status_code=200)
async def update_user(
    user_id: int,
    update_data: UpdateUserSchema,
    user: UserModel = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """
    Update user by identifier.
    Return updated user.
    """
    return await service.update_user(update_data, user, user_id)


@router.patch(
    "/change_status/{user_id}", response_model=MessageResponse, status_code=200
)
async def soft_delete(
    user_id: int,
    user: UserModel = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """
    Change user status by identifier.
    Return operation result message.
    """
    return await service.soft_delete(user, user_id)


@router.delete("/{user_id}", response_model=MessageResponse, status_code=200)
async def hard_delete(
    user_id: int,
    user: UserModel = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """
    Delete user by identifier.
    Return operation result message.
    """
    return await service.hard_delete(user, user_id)


@router.post("/token", status_code=status.HTTP_200_OK)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
):
    """
    Authenticate user with provided credentials.
    Return access token.
    """
    return await service.authorization(form_data)
