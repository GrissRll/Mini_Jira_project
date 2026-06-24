from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "postgresql+asyncpg://jira_user:jira_admin@localhost:5432/jira_db"

async_engine = create_async_engine(url=DATABASE_URL, echo=True)  # поменять после тестирования на False

async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


