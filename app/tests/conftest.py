import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.depends import get_db
from app.main import app as prod_app
from app.models.base import Base
import asyncio

TEST_DATABASE_URL = "postgresql+asyncpg://test_jira_user:test_jira_admin@localhost:5432/test_jira_db"


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
    print("engine loop", id(asyncio.get_running_loop()))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture
async def async_session_maker(test_engine):
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def app_test(async_session_maker):
    async def _get_db():
        async with async_session_maker() as session:
            try:
                yield session
            finally:
                await session.rollback()

    prod_app.dependency_overrides[get_db] = _get_db
    yield prod_app
    prod_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app_test: FastAPI):
    transport = ASGITransport(app=app_test)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
