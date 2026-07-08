import pytest
from app.models.users import User as UserModel
from app.models.projects import Project as ProjectModel
from app.core.auth import hash_password
from app.tests.data.users import user_data_ok, user_data_user2
from app.tests.data.projects import project_data_ok


@pytest.fixture(scope="function")
async def create_users_with_project(async_session_maker):
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
        await session.flush()
        project = ProjectModel(**project_data_ok)
        session.add(project)
        await session.commit()
        await session.close()
