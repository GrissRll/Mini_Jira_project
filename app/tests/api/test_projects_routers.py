import pytest
from sqlalchemy import insert
from app.models.projects import Project as ProjectModel
from app.tests.data.projects import project_data_ok, project_data_second


@pytest.mark.asyncio
async def test_get_projects_router_200(client, create_user_fix, async_session_maker):
    async with async_session_maker() as session:
        await session.execute(
            insert(ProjectModel),
            [
                project_data_ok,
                project_data_second,
            ],
        )
        await session.commit()

    response = await client.get("/projects/")

    assert response.status_code == 200

    response_data = response.json()

    assert len(response_data) == 2

    assert response_data[0]["title"] == project_data_ok["title"]

    assert response_data[1]["title"] == project_data_second["title"]


@pytest.mark.asyncio
async def test_get_projects_router_empty(client):
    response = await client.get("/projects/")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_project_by_id_router_200(
    client,
    create_user_fix,
    async_session_maker,
):
    async with async_session_maker() as session:
        await session.execute(insert(ProjectModel), project_data_ok)
        await session.commit()

    response = await client.get("/projects/1")

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["id"] == 1
    assert response_data["title"] == project_data_ok["title"]
    assert response_data["description"] == project_data_ok["description"]

    assert "owner" in response_data
    assert response_data["owner"]["id"] == project_data_ok["owner_id"]


@pytest.mark.asyncio
async def test_get_project_by_id_router_404(client):
    response = await client.get("/projects/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found or inactive."


@pytest.mark.asyncio
async def test_get_project_by_id_router_inactive_project(
    client,
    create_user_fix,
    async_session_maker,
):
    async with async_session_maker() as session:
        await session.execute(
            insert(ProjectModel),
            {
                **project_data_ok,
                "is_active": False,
            },
        )
        await session.commit()

    response = await client.get("/projects/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found or inactive."


@pytest.mark.asyncio
async def test_get_owner_projects_router_200(
    client,
    create_user_fix,
    async_session_maker,
):
    other_owner_project = {
        **project_data_second,
        "owner_id": 2,
    }
    async with async_session_maker() as session:
        await session.execute(
            insert(ProjectModel),
            [project_data_ok, other_owner_project],
        )
        await session.commit()

    response = await client.get("/projects/owner/1")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "title": project_data_ok["title"],
        }
    ]


@pytest.mark.asyncio
async def test_get_owner_projects_router_404(client):
    response = await client.get("/projects/owner/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found or inactive."


@pytest.mark.asyncio
async def test_get_owner_projects_router_skips_inactive_projects(
    client,
    create_user_fix,
    async_session_maker,
):
    async with async_session_maker() as session:
        await session.execute(
            insert(ProjectModel),
            {
                **project_data_ok,
                "is_active": False,
            },
        )
        await session.commit()

    response = await client.get("/projects/owner/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found or inactive."


@pytest.mark.asyncio
async def test_get_owner_projects_router_422(client):
    response = await client.get("/projects/owner/not-an-integer")

    assert response.status_code == 422
