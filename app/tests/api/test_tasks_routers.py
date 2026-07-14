import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.auth import create_access_token
from app.models.projects import Project as ProjectModel
from app.models.users import User as UserModel
from app.tests.data.tasks import task_data_first
from app.tests.data.users import user_data_ok


async def build_auth_headers(
    session_maker: async_sessionmaker[AsyncSession],
) -> dict[str, str]:
    async with session_maker() as session:
        user = await session.scalar(
            select(UserModel).where(UserModel.email == user_data_ok["email"])
        )
    assert user is not None
    access_token = create_access_token(data={"sub": user.email, "id": user.id})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.mark.asyncio
async def test_get_task_by_id_router_200(
    client,
    create_tasks,
    async_session_maker,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.get("/tasks/1", headers=headers)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == 1
    assert response_data["title"] == task_data_first["title"]
    assert response_data["description"] == task_data_first["description"]
    assert response_data["project_id"] == task_data_first["project_id"]
    assert response_data["worker_id"] == task_data_first["worker_id"]
    assert response_data["task_status"] == "waited"
    assert response_data["created_at"] is not None
    assert response_data["updated_at"] is not None
    assert response_data["finished_at"] is None


@pytest.mark.asyncio
async def test_get_task_by_id_router_401(client):
    response = await client.get("/tasks/1")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.asyncio
async def test_get_task_by_id_router_404(
    client,
    create_tasks,
    async_session_maker,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.get("/tasks/999", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found or inactive"


@pytest.mark.asyncio
async def test_get_task_by_id_router_inactive_task_404(
    client,
    create_tasks,
    async_session_maker,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.get("/tasks/3", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found or inactive"


@pytest.mark.asyncio
async def test_get_task_by_id_router_inactive_project_404(
    client,
    create_tasks,
    async_session_maker,
):
    async with async_session_maker() as session:
        project = await session.get(ProjectModel, 1)
        assert project is not None
        project.is_active = False
        await session.commit()
    headers = await build_auth_headers(async_session_maker)

    response = await client.get("/tasks/1", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found or inactive."


@pytest.mark.asyncio
@pytest.mark.parametrize("task_id", ["not-an-integer", "0", "-1"])
async def test_get_task_by_id_router_422(
    client,
    create_tasks,
    async_session_maker,
    task_id,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.get(f"/tasks/{task_id}", headers=headers)

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
