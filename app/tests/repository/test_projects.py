import pytest
from app.repositories.projects import ProjectRepository
from app.models.projects import Project as ProjectModel
from app.tests.data.projects import project_data_ok, project_data_update, project_data_update_empty
from sqlalchemy import select


def test_build_filters():
    repo = ProjectRepository(None)

    filters = repo.build_filters(owner_id=1, project_id=2)

    assert len(filters) == 3


@pytest.mark.asyncio
async def test_create(async_session_maker, create_user):
    async with async_session_maker() as session:
        repo = ProjectRepository(session)

        project = await repo.create(project_data_ok)
        await session.commit()

        db_project = (
            await session.scalars(select(ProjectModel))
        ).first()

        assert project == db_project
        assert db_project.title == project_data_ok["title"]
        assert db_project.description == project_data_ok["description"]


@pytest.mark.asyncio
async def test_select_by_id(async_session_maker, create_user):
    async with async_session_maker() as session:
        repo = ProjectRepository(session)

        await repo.create(project_data_ok)
        await session.commit()

        project = await repo.select_one(project_id=1)

        assert project is not None
        assert project.title == project_data_ok["title"]


@pytest.mark.asyncio
async def test_select_by_id_none(async_session_maker, create_user):
    async with async_session_maker() as session:
        repo = ProjectRepository(session)

        project = await repo.select_one(100)

        assert project is None


@pytest.mark.asyncio
async def test_select_all(async_session_maker, create_user):
    async with async_session_maker() as session:
        repo = ProjectRepository(session)

        await repo.create(project_data_ok)

        await repo.create(
            {
                "title": "Project 2",
                "description": "Test",
                "owner_id": 1,
            }
        )

        await session.commit()

        projects = await repo.select_many()

        assert len(projects) == 2


@pytest.mark.asyncio
async def test_select_all_for_owner(async_session_maker, create_user):
    async with async_session_maker() as session:
        repo = ProjectRepository(session)

        await repo.create(project_data_ok)

        await repo.create(
            {
                "title": "Second",
                "description": "Test",
                "owner_id": 2,
            }
        )

        await session.commit()

        projects = await repo.select_many(owner_id=1)

        assert len(projects) == 1
        assert projects[0].owner_id == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expected,arg",
    [
        (
                {
                    "title": project_data_update["title"],
                    "description": project_data_update["description"],
                },
                project_data_update,
        ),
        (
                {
                    "title": project_data_ok["title"],
                    "description": project_data_ok["description"],
                },
                project_data_update_empty,
        ),
    ],
)
async def test_update(async_session_maker, create_user, expected, arg):
    async with async_session_maker() as session:
        repo = ProjectRepository(session)

        await repo.create(project_data_ok)
        await session.commit()

        project = (
            await session.scalars(select(ProjectModel))
        ).first()

        updated_project = await repo.update(arg, project)
        await session.commit()
        print(updated_project.title)
        print(updated_project.description)

        db_project = (
            await session.scalars(select(ProjectModel))
        ).first()

        assert updated_project == db_project
        assert db_project.title == expected["title"]
        assert db_project.description == expected["description"]


@pytest.mark.asyncio
async def test_soft_delete(async_session_maker, create_user):
    async with async_session_maker() as session:
        repo = ProjectRepository(session)

        await repo.create(project_data_ok)
        await session.commit()

        await repo.soft_delete(1)
        await session.commit()

        project = (
            await session.scalars(select(ProjectModel))
        ).first()

        assert project.is_active is False


@pytest.mark.asyncio
async def test_hard_delete(async_session_maker, create_user):
    async with async_session_maker() as session:
        repo = ProjectRepository(session)

        await repo.create(project_data_ok)
        await session.commit()

        await repo.hard_delete(1)
        await session.commit()

        project = (
            await session.scalars(select(ProjectModel))
        ).first()

        assert project is None


@pytest.mark.asyncio
async def test_select_all_skip_inactive(async_session_maker, create_user):
    async with async_session_maker() as session:
        repo = ProjectRepository(session)

        await repo.create(project_data_ok)
        await session.commit()

        await repo.soft_delete(1)
        await session.commit()

        projects = await repo.select_many()

        assert projects == []
