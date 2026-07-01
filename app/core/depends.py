from fastapi import Depends
from app.repositories.users import UserRepository
from app.services.users_services import UserService
from .database import async_session_maker
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async generator for session object"""
    async with async_session_maker() as session:
        yield session


async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


async def get_user_service(user_repo:UserRepository = Depends(get_user_repository)):
    return UserService(user_repository=user_repo)
