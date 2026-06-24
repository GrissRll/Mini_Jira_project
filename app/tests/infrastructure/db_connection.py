import asyncio
from app.core.database import async_session_maker
from sqlalchemy import text


async def check_connection():
    async with async_session_maker() as session:
        stmt = text("SELECT 1")
        result = await session.scalar(stmt)
        return result

assert asyncio.run(check_connection()) == 1

