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
    email: str = user_data_ok["email"],
) -> dict[str, str]:
    async with session_maker() as session:
        user = await session.scalar(
            select(UserModel).where(UserModel.email == email)
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


@pytest.mark.asyncio
async def test_get_tasks_router_200(
    client,
    create_tasks,
    async_session_maker,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.get("/tasks/", headers=headers)

    assert response.status_code == 200
    assert [task["id"] for task in response.json()] == [1, 2]
    assert set(response.json()[0]) == {"id", "title", "project_id", "created_at"}


@pytest.mark.asyncio
async def test_get_tasks_router_requires_authentication(client):
    response = await client.get("/tasks/")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_tasks_router_applies_filters(
    client,
    create_tasks,
    async_session_maker,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.get(
        "/tasks/",
        params={"worker_id": 2, "title": task_data_first["title"]},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_tasks_router_applies_ordering(
    client,
    create_tasks,
    async_session_maker,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.get(
        "/tasks/",
        params={"columns": "id", "direction": "desc"},
        headers=headers,
    )

    assert response.status_code == 200
    assert [task["id"] for task in response.json()] == [2, 1]


@pytest.mark.asyncio
async def test_get_tasks_router_accepts_multiple_ordering_columns(
    client,
    create_tasks,
    async_session_maker,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.get(
        "/tasks/",
        params=[("columns", "title"), ("columns", "created_at")],
        headers=headers,
    )

    assert response.status_code == 200
    assert [task["id"] for task in response.json()] == [2, 1]


@pytest.mark.asyncio
async def test_get_tasks_router_applies_pagination(
    client,
    create_tasks,
    async_session_maker,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.get(
        "/tasks/",
        params={"page_num": 2, "page_size": 1},
        headers=headers,
    )

    assert response.status_code == 200
    assert [task["id"] for task in response.json()] == [2]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params",
    [
        {"columns": "unknown"},
        {"direction": "unknown"},
        {"page_num": 0},
        {"page_size": 100},
        {"worker_id": 0},
    ],
)
async def test_get_tasks_router_rejects_invalid_query_params(
    client,
    create_tasks,
    async_session_maker,
    params,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.get("/tasks/", params=params, headers=headers)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_router_201(
    client,
    create_users_with_project,
    async_session_maker,
):
    headers = await build_auth_headers(async_session_maker)
    payload = {
        "title": "API created task",
        "description": "Created through API",
        "project_id": 1,
        "worker_id": 2,
    }

    response = await client.post("/tasks/", json=payload, headers=headers)

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["id"] is not None
    assert response_data["title"] == payload["title"]
    assert response_data["description"] == payload["description"]
    assert response_data["project_id"] == payload["project_id"]
    assert response_data["worker_id"] == payload["worker_id"]
    assert response_data["task_status"] == "waited"


@pytest.mark.asyncio
async def test_create_task_router_401(client):
    response = await client.post(
        "/tasks/",
        json={"title": "Unauthorized task", "project_id": 1},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_create_task_router_403_for_non_owner(
    client,
    create_users_with_project,
    async_session_maker,
):
    headers = await build_auth_headers(
        async_session_maker,
        email="ivan.petrov@example.comV2",
    )

    response = await client.post(
        "/tasks/",
        json={"title": "Forbidden API task", "project_id": 1},
        headers=headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Only project owner can create task"


@pytest.mark.asyncio
async def test_create_task_router_404_for_missing_project(
    client,
    create_users_with_project,
    async_session_maker,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.post(
        "/tasks/",
        json={"title": "Missing project task", "project_id": 999},
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found or inactive."


@pytest.mark.asyncio
async def test_create_task_router_404_for_missing_worker(
    client,
    create_users_with_project,
    async_session_maker,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.post(
        "/tasks/",
        json={"title": "Missing worker task", "project_id": 1, "worker_id": 999},
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_create_task_router_409_for_duplicate_title(
    client,
    create_users_with_project,
    async_session_maker,
):
    headers = await build_auth_headers(async_session_maker)
    payload = {"title": "Duplicate API task", "project_id": 1}
    first_response = await client.post("/tasks/", json=payload, headers=headers)

    duplicate_response = await client.post("/tasks/", json=payload, headers=headers)

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == "Task already exists"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {"title": "", "project_id": 1},
        {"title": "Valid title", "project_id": 0},
        {"title": "Valid title", "project_id": 1, "worker_id": 0},
    ],
)
async def test_create_task_router_422(
    client,
    create_users_with_project,
    async_session_maker,
    payload,
):
    headers = await build_auth_headers(async_session_maker)

    response = await client.post("/tasks/", json=payload, headers=headers)

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
