import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.config import get_settings
from app.core.depends import get_db
from app.main import create_application
from app.models.base import Base
import asyncio

TEST_DATABASE_URL = (
    "postgresql+asyncpg://test_user:test_pass@localhost:5433/test_db"
)


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
    prod_app = create_application()
    prod_app.dependency_overrides[get_db] = _get_db

    async with prod_app.router.lifespan_context(prod_app):
        yield prod_app
    prod_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app_test: FastAPI):
    transport = ASGITransport(app=app_test)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
