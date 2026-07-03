import pytest
from app.models.users import User as UserModel
from app.tests.data.users import user_data_ok
from sqlalchemy import select
from app.core.auth import hash_password

pytest_plugins = [
    "app.tests.fixtures.users",
]


@pytest.fixture(scope="function")
async def create_user_fix(async_session_maker):
    async with async_session_maker() as session:
        data = {"user_name": user_data_ok["user_name"],
                "email": user_data_ok["user_name"],
                "hashed_password": hash_password(user_data_ok["user_name"])}
        await session.execute(select(UserModel, data))
        await session.commit()
        await session.close()
