import pytest
from app.tests.data.users_data.repo_data import users_data
from app.models.users import User as UserModel
from sqlalchemy import insert


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
        await session.close()
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
