import pytest
from app.repositories.users import UserRepository
from fastapi.security import OAuth2PasswordRequestForm
from app.core.auth import hash_password
from app.models.users import User as UserModel
from app.schemas.users import CreateUserSchema, UpdateUserSchema
from app.exeptions.units.users_exeptions import (
    UserEmailAlreadyExistsError,
    UserNameAlreadyExistsError,
    UserNotFoundError,
    UserForbiddenError,
    UserAuthorizationError,
)
from sqlalchemy import insert, select

from app.services.users_services import UserService
from app.tests.data.users import (
    users_data,
    user_data_ok,
    user_data_update_all,
    user_data_update_existing_email,
    user_data_update_existing_user_name,
    user_data_ok_password_v2,
    user_data_exist_email_v2,
    user_data_exist_name_v2,
)


@pytest.mark.asyncio
async def test_create_user_service_ok(async_session_maker):
    async with async_session_maker() as session:
        user_schema = CreateUserSchema(**user_data_ok_password_v2)
    service = UserService(UserRepository(session))
    result = await service.create_user(user_schema)
    assert result is not None
    assert type(result) == UserModel


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expected, arg",
    [
        (UserNameAlreadyExistsError, user_data_exist_name_v2),
        (UserEmailAlreadyExistsError, user_data_exist_email_v2),
    ],
)
async def test_create_user_service_400(async_session_maker, expected, arg):
    async with async_session_maker() as session:
        user_schema = CreateUserSchema(**user_data_ok_password_v2)
        service = UserService(UserRepository(session))
        await service.create_user(user_schema)
        with pytest.raises(expected):
            user_schema = CreateUserSchema(**arg)
            await service.create_user(user_schema)


@pytest.mark.asyncio
@pytest.mark.parametrize("expected, arg", [(len(users_data), users_data), (0, [])])
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
        user = (
            await session.scalars(select(UserModel).where(UserModel.id == 1))
        ).first()
        assert user.user_name == user_data_update_all["user_name"]
        assert user.email == user_data_update_all["email"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expected, arg",
    [
        (UserNameAlreadyExistsError, user_data_update_existing_user_name),
        (UserEmailAlreadyExistsError, user_data_update_existing_email),
    ],
)
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


@pytest.mark.asyncio
async def test_soft_delete_ok(async_session_maker):
    async with async_session_maker() as session:
        service = UserService(UserRepository(session))
        await service.create_user(CreateUserSchema(**user_data_ok_password_v2))
        user = (await session.scalars(select(UserModel))).first()
        response = await service.soft_delete(user, user.id)
        await session.refresh(user)
        assert user.is_active is False
        assert response == {
            "message": f"User {user.user_name} change status to inactive"
        }


@pytest.mark.asyncio
async def test_soft_delete_forbidden(async_session_maker):
    async with async_session_maker() as session:
        service = UserService(UserRepository(session))

        await service.create_user(CreateUserSchema(**user_data_ok_password_v2))

        user = (await session.scalars(select(UserModel))).first()

        with pytest.raises(UserForbiddenError):
            await service.soft_delete(user, user.id + 1)


@pytest.mark.asyncio
async def test_hard_delete_ok(async_session_maker):
    async with async_session_maker() as session:
        service = UserService(UserRepository(session))

        await service.create_user(CreateUserSchema(**user_data_ok_password_v2))

        user = (await session.scalars(select(UserModel))).first()

        response = await service.hard_delete(user, user.id)

        deleted_user = (await session.scalars(select(UserModel))).first()

        assert deleted_user is None
        assert response == {"message": f"User {user.user_name} was deleted!"}


@pytest.mark.asyncio
async def test_hard_delete_forbidden(async_session_maker):
    async with async_session_maker() as session:
        service = UserService(UserRepository(session))

        await service.create_user(CreateUserSchema(**user_data_ok_password_v2))

        user = (await session.scalars(select(UserModel))).first()

        with pytest.raises(UserForbiddenError):
            await service.hard_delete(user, user.id + 1)


@pytest.mark.asyncio
async def test_authorization_ok(async_session_maker):
    async with async_session_maker() as session:
        service = UserService(UserRepository(session))
        await session.execute(
            insert(UserModel).values(
                user_name=user_data_ok["user_name"],
                email=user_data_ok["email"],
                hashed_password=hash_password(user_data_ok["hashed_password"]),
            )
        )
        await session.commit()
        result = await service.authorization(
            OAuth2PasswordRequestForm(
                username=user_data_ok["email"], password=user_data_ok["hashed_password"]
            )
        )
        assert result is not None


@pytest.mark.asyncio
async def test_authorization_fail(async_session_maker):
    async with async_session_maker() as session:
        service = UserService(UserRepository(session))
        await session.execute(
            insert(UserModel).values(
                user_name=user_data_ok["user_name"],
                email=user_data_ok["email"],
                hashed_password=hash_password(user_data_ok["hashed_password"]),
            )
        )

        await session.commit()
        with pytest.raises(UserAuthorizationError):
            await service.authorization(
                OAuth2PasswordRequestForm(
                    username=user_data_ok["email"], password="123"
                )
            )
