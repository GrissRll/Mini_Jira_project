import pytest
from app.models.users import User as UserModel
from app.core.auth import hash_password
from app.tests.data.users import user_data_ok, user_data_user2


@pytest.fixture(scope="function")
async def create_user(async_session_maker):
    async with async_session_maker() as session:
        users = []
        for user in (user_data_ok, user_data_user2):
            data = {
                "user_name": user["user_name"],
                "email": user["email"],
                "hashed_password": hash_password(user["hashed_password"]),
            }
            users.append(UserModel(**data))

        session.add_all(users)
        await session.commit()
        await session.close()
