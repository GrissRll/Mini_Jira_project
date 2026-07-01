import fastapi.exceptions
import pytest
from app.repositories.users import UserRepository
from app.models.users import User as UserModel
from app.schemas.users import CreateUserSchema
from app.exeptions.users_exeptions import UserForbiddenError, UserAlreadyExistsError, UserEmailAlreadyExistsError, \
    UserNameAlreadyExistsError, UserNotFoundError
from sqlalchemy import select, insert, delete

from app.services.users_services import UserService
from app.tests.data.users_data.repo_data import users_data, user_data_ok, user_data_exist_email, user_data_exist_name



@pytest.mark.asyncio
async def test_create_user_service_ok(async_session_maker):
    async with async_session_maker() as session:
        user_schema = CreateUserSchema(**user_data_ok)
    service = UserService(UserRepository(session))
    result = await service.create_user(user_schema)
    assert result is not None
    assert type(result) == UserModel


@pytest.mark.asyncio
@pytest.mark.parametrize("expected, arg", [
    (UserNameAlreadyExistsError, user_data_exist_name),
    (UserEmailAlreadyExistsError, user_data_exist_email)
])
async def test_create_user_service_400(async_session_maker, expected, arg):
    async with async_session_maker() as session:
        user_schema = CreateUserSchema(**user_data_ok)
        service = UserService(UserRepository(session))
        await service.create_user(user_schema)
        with pytest.raises(expected):
            user_schema = CreateUserSchema(**arg)
            await service.create_user(user_schema)


@pytest.mark.asyncio
@pytest.mark.parametrize("expected, arg", [
    (len(users_data), users_data),
    (0, [])
])
async def test_get_all_users_service(async_session_maker, expected, arg):
    async with async_session_maker() as session:
        if arg:
            await session.execute(insert(UserModel), arg)
            await session.commit()
        service = UserService(UserRepository(session))
        result = await service.get_all_users()
        print(result)
        assert result is not None
        assert len(result) == expected


@pytest.mark.asyncio
async def test_get_user_by_id_service_ok(async_session_maker):
    async with async_session_maker() as session:
        await session.execute(insert(UserModel), user_data_ok)
        await session.commit()
        service = UserService(UserRepository(session))
        result = await service.get_user_by_id(1)
        assert result is not None
        assert result.user_name == user_data_ok["user_name"]


@pytest.mark.asyncio
async def test_get_user_by_id_service_404(async_session_maker):
    async with async_session_maker() as session:
        with pytest.raises(UserNotFoundError):
            service = UserService(UserRepository(session))
            await service.get_user_by_id(1)

