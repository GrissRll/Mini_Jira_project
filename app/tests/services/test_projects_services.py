import pytest
from app.services.projects_service import ProjectService
from app.repositories.projects import ProjectRepository
from app.tests.data.projects import project_data_ok, project_data_second
from app.exeptions.units.projects_exeptions import ProjectNotFoundError,ProjectNameExistingError


@pytest.mark.asyncio
async def test_get_projects(async_session_maker, create_user_fix):
    async with async_session_maker() as session:
        repo = ProjectRepository(session)
        service = ProjectService(repo)

        await repo.create(project_data_ok)
        await repo.create(project_data_second)
        await session.commit()

        projects = await service.get_projects()

        assert len(projects) == 2
        assert projects[0].title == project_data_ok["title"]
        assert projects[1].title == project_data_second["title"]

@pytest.mark.asyncio
async def test_get_projects_empty(async_session_maker):
    async with async_session_maker() as session:
        service = ProjectService(ProjectRepository(session))

        projects = await service.get_projects()

        assert projects == []

@pytest.mark.asyncio
async def test_get_project(async_session_maker, create_user_fix):
    async with async_session_maker() as session:
        repo = ProjectRepository(session)
        service = ProjectService(repo)

        await repo.create(project_data_ok)
        await session.commit()

        project = await service.get_project(1)

        assert project.id == 1
        assert project.title == project_data_ok["title"]

@pytest.mark.asyncio
async def test_get_project_404(async_session_maker):
    async with async_session_maker() as session:
        service = ProjectService(ProjectRepository(session))

        with pytest.raises(ProjectNotFoundError):
            await service.get_project(1)

@pytest.mark.asyncio
async def test_get_owner_projects(async_session_maker, create_user_fix):
    async with async_session_maker() as session:
        repo = ProjectRepository(session)
        service = ProjectService(repo)

        await repo.create(project_data_ok)
        await repo.create(project_data_second)
        await session.commit()

        projects = await service.get_owner_projects(1)

        assert len(projects) == 2
        assert all(project.owner_id == 1 for project in projects)

@pytest.mark.asyncio
async def test_get_owner_projects_not_found(async_session_maker):
    async with async_session_maker() as session:
        service = ProjectService(ProjectRepository(session))

        with pytest.raises(ProjectNotFoundError):
            await service.get_owner_projects(1)