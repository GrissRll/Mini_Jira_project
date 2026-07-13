import pytest
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.auth import create_access_token
from app.models.projects import Project as ProjectModel
from app.models.users import User as UserModel
from app.tests.data.projects import (
    project_data_ok,
    project_data_second,
    project_data_update,
)
from app.tests.data.users import user_data_ok, user_data_user2


async def build_auth_headers(
    session_maker: async_sessionmaker[AsyncSession],
    email: str = user_data_ok["email"],
) -> dict[str, str]:
    async with session_maker() as session:
        user = (
            await session.scalars(
                select(UserModel).where(UserModel.email == email)
            )
        ).first()
    assert user is not None
    access_token = create_access_token(data={"sub": user.email, "id": user.id})
    return {"Authorization": f"Bearer {access_token}"}


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


@pytest.mark.asyncio
async def test_create_project_router_201(
    client,
    create_user_fix,
    async_session_maker,
):
    headers = await build_auth_headers(async_session_maker)
    project_data = {
        "title": project_data_ok["title"],
        "description": project_data_ok["description"],
    }

    response = await client.post("/projects/", json=project_data, headers=headers)

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["title"] == project_data["title"]
    assert response_data["description"] == project_data["description"]
    assert response_data["owner"]["email"] == user_data_ok["email"]
    assert response_data["created_at"] is not None

    async with async_session_maker() as session:
        project = await session.scalar(
            select(ProjectModel).where(ProjectModel.id == response_data["id"])
        )

    assert project is not None
    assert project.title == project_data["title"]
    assert project.description == project_data["description"]
    assert project.owner_id == response_data["owner"]["id"]


@pytest.mark.asyncio
async def test_create_project_router_401(client):
    response = await client.post(
        "/projects/",
        json={
            "title": project_data_ok["title"],
            "description": project_data_ok["description"],
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "project_data",
    [
        {},
        {"title": "Jira"},
        {"title": "x" * 101},
        {"title": "Valid project", "description": "x" * 2001},
    ],
)
async def test_create_project_router_422(
    client,
    create_user_fix,
    async_session_maker,
    project_data,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.post("/projects/", json=project_data, headers=headers)

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


@pytest.mark.asyncio
async def test_create_project_router_409(
    client,
    create_user_fix,
    async_session_maker,
):
    async with async_session_maker() as session:
        await session.execute(insert(ProjectModel), project_data_ok)
        await session.commit()
    headers = await build_auth_headers(async_session_maker)

    response = await client.post(
        "/projects/",
        json={
            "title": project_data_ok["title"],
            "description": "Another description",
        },
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Project name already existing."


@pytest.mark.asyncio
async def test_update_project_router_201(
    client,
    create_users_with_project,
    async_session_maker,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.patch(
        "/projects/1",
        json=project_data_update,
        headers=headers,
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == 1
    assert response_data["title"] == project_data_update["title"]
    assert response_data["description"] == project_data_update["description"]
    assert response_data["owner"]["id"] == 1

    async with async_session_maker() as session:
        project = await session.get(ProjectModel, 1)

    assert project is not None
    assert project.title == project_data_update["title"]
    assert project.description == project_data_update["description"]


@pytest.mark.asyncio
async def test_update_project_router_partial_update(
    client,
    create_users_with_project,
    async_session_maker,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.patch(
        "/projects/1",
        json={"description": project_data_update["description"]},
        headers=headers,
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["title"] == project_data_ok["title"]
    assert response_data["description"] == project_data_update["description"]


@pytest.mark.asyncio
async def test_update_project_router_401(client):
    response = await client.patch(
        "/projects/1",
        json=project_data_update,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.asyncio
async def test_update_project_router_403(
    client,
    create_users_with_project,
    async_session_maker,
):
    headers = await build_auth_headers(
        async_session_maker,
        email=user_data_user2["email"],
    )

    response = await client.patch(
        "/projects/1",
        json=project_data_update,
        headers=headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Only owner can update project."


@pytest.mark.asyncio
async def test_update_project_router_404(
    client,
    create_user_fix,
    async_session_maker,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.patch(
        "/projects/999",
        json=project_data_update,
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found or inactive."


@pytest.mark.asyncio
async def test_update_project_router_inactive_project_404(
    client,
    create_users_with_project,
    async_session_maker,
):
    async with async_session_maker() as session:
        project = await session.get(ProjectModel, 1)
        assert project is not None
        project.is_active = False
        await session.commit()
    headers = await build_auth_headers(async_session_maker)

    response = await client.patch(
        "/projects/1",
        json=project_data_update,
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found or inactive."


@pytest.mark.asyncio
async def test_update_project_router_409_existing_title(
    client,
    create_users_with_project,
    async_session_maker,
):
    async with async_session_maker() as session:
        await session.execute(insert(ProjectModel), project_data_second)
        await session.commit()
    headers = await build_auth_headers(async_session_maker)

    response = await client.patch(
        "/projects/1",
        json={"title": project_data_second["title"]},
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Project name already existing."


@pytest.mark.asyncio
async def test_update_project_router_409_null_title(
    client,
    create_users_with_project,
    async_session_maker,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.patch(
        "/projects/1",
        json={"title": None},
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Project name can't be null."


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("project_id", "project_data"),
    [
        ("not-an-integer", project_data_update),
        (1, {"title": "Jira"}),
        (1, {"title": "x" * 101}),
        (1, {"description": "x" * 2001}),
    ],
)
async def test_update_project_router_422(
    client,
    create_users_with_project,
    async_session_maker,
    project_id,
    project_data,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.patch(
        f"/projects/{project_id}",
        json=project_data,
        headers=headers,
    )

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
