import pytest
from app.repositories.users import UserRepository
from app.models.users import User as UserModel
from app.schemas.users import CreateUserSchema, UpdateUserSchema
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from app.tests.data.users_data.repo_data import users_data, user_data_ok, user_data_update_all, \
    user_data_update_email, user_data_update_nothing


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


@pytest.mark.asyncio
@pytest.mark.parametrize("expected, arg", [
    ({"user_name": user_data_update_all["user_name"], "email": user_data_update_all["email"]}, user_data_update_all),
    ({"user_name": user_data_ok["user_name"], "email": user_data_update_email["email"]}, user_data_update_email),
    ({"user_name": user_data_ok["user_name"], "email": user_data_ok["email"]}, user_data_update_nothing)
])
async def test_update(async_session_maker, expected, arg):
    async with async_session_maker() as session:
        repo = UserRepository(session)
        await session.execute(insert(UserModel), user_data_ok)
        await session.commit()
        user = (await session.scalars(select(UserModel))).first()

        updated_user = await repo.update(user, arg)
        assert updated_user.user_name == expected["user_name"]
        assert updated_user.email == expected["email"]
        await session.commit()
        user = (await session.scalars(select(UserModel))).first()
        assert user.user_name == expected["user_name"]
        assert user.email == expected["email"]

@pytest.mark.asyncio
async def test_soft_delete(async_session_maker):
    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        await session.execute(insert(UserModel), user_data_ok)
        await session.commit()
        await user_repo.soft_delete(1)
        await session.commit()
        active_user = await session.scalars(select(UserModel).where(UserModel.id == 1, UserModel.is_active == True))
        active_user = active_user.first()
        user_inactive = await session.scalars(select(UserModel).where(UserModel.id == 1))
        user_inactive = user_inactive.first()
        assert active_user is None
        assert user_inactive.is_active == False


@pytest.mark.asyncio
async def test_hard_delete(async_session_maker):
    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        await session.execute(insert(UserModel), user_data_ok)
        await session.commit()
        await user_repo.hard_delete(1)
        await session.commit()
        active_user = await session.scalars(select(UserModel).where(UserModel.id == 1, UserModel.is_active == True))
        active_user = active_user.first()
        user_inactive = await session.scalars(select(UserModel).where(UserModel.id == 1))
        user_inactive = user_inactive.first()
        assert active_user is None
        assert user_inactive is None
