import pytest

from app.repositories.users import UserRepository
from app.models.users import User as UserModel
from app.schemas.users import CreateUserSchema
from sqlalchemy import select, insert, delete
from sqlalchemy.exc import IntegrityError
from app.tests.data.users_data.repo_data import users_data, user_data_ok, user_data_exist_email, user_data_exist_name
from app.services.users_services import create_user_services, get_all_users_service
from fastapi.exceptions import HTTPException


@pytest.mark.asyncio
async def test_create_user_service_ok(async_session_maker):
    async with async_session_maker() as session:
        user_schema = CreateUserSchema(**user_data_ok)
    result = await create_user_services(session, user_schema)
    assert result is not None
    assert type(result) == UserModel


@pytest.mark.asyncio
@pytest.mark.parametrize("expected, arg", [
    ({"status_code": 400, "detail": "User name already existing"}, user_data_exist_name),
    ({"status_code": 400, "detail": "Email already existing"}, user_data_exist_email)
])
async def test_create_user_service_400(async_session_maker, expected, arg):
    async with async_session_maker() as session:
        user_schema = CreateUserSchema(**user_data_ok)
        await create_user_services(session, user_schema)
        with pytest.raises(HTTPException) as exc_info:
            user_schema = CreateUserSchema(**arg)
            await create_user_services(session, user_schema)
            exc = exc_info.value
            assert exc.status_code == expected["status_code"]
            assert exc.detail == expected["detail"]


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
        result = await get_all_users_service(session)
        print(result)
        assert result is not None
        assert len(result) == expected
