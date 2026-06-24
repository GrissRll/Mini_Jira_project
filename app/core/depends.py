from .database import async_session_maker
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async generator for session object"""
    async with async_session_maker() as session:
        yield session
