from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
)


def create_engine(database_url: str) -> AsyncEngine:
    async_engine = create_async_engine(url=database_url, echo=True)
    return async_engine


def create_async_session(async_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    async_session_maker = async_sessionmaker(
        bind=async_engine, expire_on_commit=False, class_=AsyncSession
    )
    return async_session_maker
