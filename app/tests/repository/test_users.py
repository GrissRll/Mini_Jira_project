import pytest
from app.repositories.users import UserRepository
from app.models.users import User as UserModel
from app.schemas.users import CreateUserSchema
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from app.tests.data.users_data.repo_data import users_data



@pytest.mark.asyncio
async def test_create_user_ok(async_session_maker):
    async with async_session_maker() as session:
        repo = UserRepository(session)
        user_data = CreateUserSchema(email="test_user@mail.com", user_name="Diplodok Ivanov")
        await repo.create(user_data)
        await session.commit()

        result = await session.scalars(select(UserModel))
        result = result.all()
    assert result is not None
    assert len(result) == 1
    assert result[0].user_name == "Diplodok Ivanov"


@pytest.mark.asyncio
async def test_create_existing_user(async_session_maker):
    async with async_session_maker() as session:
        repo = UserRepository(session)
        user_data = CreateUserSchema(email="test_user@mail.com", user_name="Diplodok Ivanov")
        await repo.create(user_data)
        await session.commit()
        with pytest.raises(IntegrityError):
            user_data = CreateUserSchema(email="test_user@mail.com", user_name="Diplodok Ivanov")
            await repo.create(user_data)
            await session.flush()
@pytest.mark.asyncio
async def test_get_all_users_ok(async_session_maker):
    async with async_session_maker() as session:
        repo = UserRepository(session)
        await session.execute(insert(UserModel), users_data)
        await session.commit()
        res = await repo.get_all()
        assert len(res) == len(users_data)

@pytest.mark.asyncio
async def test_get_all_users_failed(async_session_maker):
    async with async_session_maker() as session:
        repo = UserRepository(session)
        await session.execute(insert(UserModel), users_data)
        await session.rollback()
        res = await repo.get_all()
        assert len(res) != len(users_data)
        assert len(res) == 0



