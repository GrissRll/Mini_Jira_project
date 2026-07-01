from fastapi import APIRouter, Depends
from sqlalchemy.util import await_only

from app.core.depends import get_db
from app.models.users import User as UserModel
from app.schemas.users import UserResponseSchema, CreateUserSchema
from app.services.users_services import UserService
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/", status_code=200, response_model=List[UserResponseSchema])
async def get_all_users(db: AsyncSession = Depends(get_db),
                        page_num: int = 1,
                        page_size: int = 10):
    return await get_all_users_service(db, page_num, page_size)


@router.post("/", status_code=201, response_model=UserResponseSchema)
async def create_new_user(user: CreateUserSchema, db: AsyncSession = Depends(get_db)):
    return await create_user_services(db, user)


@router.get("/{user_id}", status_code=200, response_model=UserResponseSchema)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    return await get_user_by_id_service(db, user_id)
