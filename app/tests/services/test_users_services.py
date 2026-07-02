import pytest
from app.repositories.users import UserRepository
from app.models.users import User as UserModel
from app.schemas.users import CreateUserSchema, UpdateUserSchema
from app.exeptions.users_exeptions import UserEmailAlreadyExistsError, \
    UserNameAlreadyExistsError, UserNotFoundError,UserForbiddenError
from sqlalchemy import insert, select

from app.services.users_services import UserService
from app.tests.data.users import users_data, user_data_ok, user_data_exist_email, user_data_exist_name, \
    user_data_update_all, user_data_update_existing_email, user_data_update_existing_user_name


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


@pytest.mark.asyncio
async def test_update_200(async_session_maker):
    async with async_session_maker() as session:
        await session.execute(insert(UserModel), user_data_ok)
        await session.commit()
        user = (await session.scalars(select(UserModel))).first()
        service = UserService(UserRepository(session))
        await service.update_user(UpdateUserSchema(**user_data_update_all), user, 1)
        user = (await session.scalars(select(UserModel).where(UserModel.id == 1))).first()
        assert user.user_name == user_data_update_all["user_name"]
        assert user.email == user_data_update_all["email"]

@pytest.mark.asyncio
@pytest.mark.parametrize("expected, arg", [
    (UserNameAlreadyExistsError, user_data_update_existing_user_name),
    (UserEmailAlreadyExistsError, user_data_update_existing_email)
])
async def test_update_existing_data(async_session_maker, expected, arg):
    async with async_session_maker() as session:
        await session.execute(insert(UserModel), user_data_ok)
        await session.commit()
        user = (await session.scalars(select(UserModel))).first()
        service = UserService(UserRepository(session))
        with pytest.raises(expected):
            await service.update_user(UpdateUserSchema(**arg), user, 1)

@pytest.mark.asyncio
async def test_update_user_forbidden_error(async_session_maker):
    async with async_session_maker() as session:
        await session.execute(insert(UserModel), user_data_ok)
        await session.commit()
        user = (await session.scalars(select(UserModel))).first()
        service = UserService(UserRepository(session))
        with pytest.raises(UserForbiddenError):
            await service.update_user(UpdateUserSchema(**user_data_update_all), user, 2)