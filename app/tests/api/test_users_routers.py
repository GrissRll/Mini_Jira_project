import pytest
from app.tests.data.users import users_data, user_data_ok, user_data_wrong, user_data_exist_email, user_data_exist_name, \
    user_data_ok_password_v2, user_data_exist_email_v2, user_data_exist_name_v2, user_data_update_all, \
    user_data_update_existing_email, user_data_update_existing_user_name, user_data_user2, user_data_login_ok, \
    user_data_login_wrong
from app.models.users import User as UserModel
from sqlalchemy import insert, select
from app.tests.fixtures.users import create_user_fix
from app.core.auth import create_access_token


@pytest.mark.asyncio
async def test_get_all_users_200(client):
    response = await client.get("/users/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_all_users_422(client):
    params = {"page_num": 'second'}
    response = await client.get("/users/", params=params)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_all_users_200_with_users(client, async_session_maker):
    async with async_session_maker() as session:
        await session.execute(insert(UserModel), users_data)
        await session.commit()
    params = {"page_num": 2, "page_size": 3}
    response = await client.get("/users/", params=params)
    response_data = response.json()

    start = (params["page_num"] - 1) * params["page_size"]
    end = min(start + params["page_size"], len(users_data))

    expected = users_data[start:end]

    assert len(response_data) == len(expected)

    for response_user, expected_user in zip(response_data, expected):
        assert response_user["user_name"] == expected_user["user_name"]
        assert response_user["email"] == expected_user["email"]


@pytest.mark.asyncio
async def test_create_new_user_201(client):
    response = await client.post('/users/', json=user_data_ok_password_v2)
    resp_data = response.json()
    assert resp_data is not None
    assert resp_data["user_name"] == user_data_ok["user_name"]
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_new_user_422_invalid_schema(client):
    response = await client.post('/users/', json=user_data_wrong)
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize("expected, arg", [
    ({"status_code": 409, "detail": "User email already existing"}, user_data_exist_email_v2),
    ({"status_code": 409, "detail": "User name already existing"}, user_data_exist_name_v2)
])
async def test_create_new_user_409(async_session_maker, client, expected, arg):
    async with async_session_maker() as session:
        await session.execute(insert(UserModel), user_data_ok)
        await session.commit()
    response = await client.post('/users/', json=arg)
    assert response.status_code == expected["status_code"]
    assert response.json()["detail"] == expected["detail"]


@pytest.mark.asyncio
async def test_get_user_by_id_200(client, async_session_maker):
    async with async_session_maker() as session:
        await session.execute(insert(UserModel), user_data_ok)
        await session.commit()
    response = await client.get("/users/1")
    assert response is not None
    assert response.status_code == 200
    assert response.json()["user_name"] == user_data_ok["user_name"]


@pytest.mark.asyncio
async def test_get_user_by_id_422(client):
    response = await client.get('/users/dac')
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_router_200(client, create_user_fix, async_session_maker):
    async with async_session_maker() as session:
        stmt = select(UserModel)
        user = (await session.scalars(stmt)).first()
    access_token = create_access_token(data={"sub": user.email, "id": user.id})
    response = await client.patch("/users/1", json=user_data_update_all,
                                  headers={"Authorization": f"Bearer {access_token}"})
    resp_data = response.json()
    assert response.status_code == 200
    assert resp_data["email"] == user_data_update_all["email"]
    assert resp_data["user_name"] == user_data_update_all["user_name"]


@pytest.mark.asyncio
@pytest.mark.parametrize("expected, arg", [
    ({"status_code": 409, "detail": "User email already existing"}, user_data_update_existing_email),
    ({"status_code": 409, "detail": "User name already existing"}, user_data_update_existing_user_name)
])
async def test_update_router_409(client, create_user_fix, async_session_maker, expected, arg):
    async with async_session_maker() as session:
        stmt = select(UserModel).where(UserModel.email == user_data_user2["email"])
        user = (await session.scalars(stmt)).first()
    access_token = create_access_token(data={"sub": user.email, "id": user.id})

    response = await client.patch(f"/users/{user.id}", json=arg,
                                  headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == expected["status_code"]
    assert response.json()["detail"] == expected["detail"]


@pytest.mark.asyncio
async def test_update_router_403(client, create_user_fix, async_session_maker):
    async with async_session_maker() as session:
        stmt = select(UserModel).where(UserModel.email == user_data_user2["email"])
        user = (await session.scalars(stmt)).first()
    access_token = create_access_token(data={"sub": user.email, "id": user.id})

    response = await client.patch(f"/users/1", json=user_data_update_all,
                                  headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Only owner can update or delete profile"


@pytest.mark.asyncio
async def test_update_router_422(client, create_user_fix, async_session_maker):
    async with async_session_maker() as session:
        stmt = select(UserModel).where(UserModel.email == user_data_user2["email"])
        user = (await session.scalars(stmt)).first()
    access_token = create_access_token(data={"sub": user.email, "id": user.id})

    response = await client.patch(f"/users/lol", json=user_data_update_all,
                                  headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_router_401(client, async_session_maker):
    access_token = create_access_token(data={"sub": "323", "id": 2})

    response = await client.patch(f"/users/1", json=user_data_update_all,
                                  headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_soft_delete_200(client, async_session_maker, create_user_fix):
    async with async_session_maker() as session:
        stmt = select(UserModel).where(UserModel.email == user_data_ok["email"])
        user = (await session.scalars(stmt)).first()
    access_token = create_access_token(data={"sub": user.email, "id": user.id})
    response = await client.patch(f"/users/change_status/1",
                                  headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    async with async_session_maker() as session:
        users_active = (await session.scalars(select(UserModel).where(UserModel.is_active == True))).all()
        users_all = (await session.scalars(select(UserModel))).all()
    assert len(users_active) == 1
    assert len(users_all) == 2


@pytest.mark.asyncio
async def test_soft_delete_403(client, async_session_maker, create_user_fix):
    async with async_session_maker() as session:
        stmt = select(UserModel).where(UserModel.email == user_data_ok["email"])
        user = (await session.scalars(stmt)).first()
    access_token = create_access_token(data={"sub": user.email, "id": user.id})
    response = await client.patch(f"/users/change_status/222",
                                  headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Only owner can update or delete profile"


@pytest.mark.asyncio
async def test_hard_delete_200(client, async_session_maker, create_user_fix):
    async with async_session_maker() as session:
        stmt = select(UserModel).where(UserModel.email == user_data_ok["email"])
        user = (await session.scalars(stmt)).first()
    access_token = create_access_token(data={"sub": user.email, "id": user.id})
    response = await client.delete(f"/users/1",
                                   headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    async with async_session_maker() as session:
        users_active = (await session.scalars(select(UserModel).where(UserModel.is_active == True))).all()
        users_all = (await session.scalars(select(UserModel))).all()
    assert len(users_active) == len(users_all)


@pytest.mark.asyncio
async def test_hard_delete_403(client, async_session_maker, create_user_fix):
    async with async_session_maker() as session:
        stmt = select(UserModel).where(UserModel.email == user_data_ok["email"])
        user = (await session.scalars(stmt)).first()
    access_token = create_access_token(data={"sub": user.email, "id": user.id})
    response = await client.delete(f"/users/222",
                                   headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Only owner can update or delete profile"


@pytest.mark.asyncio
async def test_login_200(client, create_user_fix):
    response = await client.post("/users/token", data=user_data_login_ok)
    resp_data = response.json()
    assert response.status_code == 200
    assert resp_data.get("access_token") is not None


@pytest.mark.asyncio
async def test_login_401(client, create_user_fix):
    response = await client.post("/users/token", data=user_data_login_wrong)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"