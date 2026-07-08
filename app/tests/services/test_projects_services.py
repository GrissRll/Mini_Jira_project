import pytest
from app.services.projects_service import ProjectService
from app.repositories.projects import ProjectRepository
from app.models.users import User as UserModel
from app.tests.data.projects import (
    project_data_ok,
    project_data_second,
    project_data_update,
    null_title_data_update,
)
from app.exeptions.units.projects_exeptions import (
    ProjectNotFoundError,
    ProjectNameExistingError,
    ProjectNotOwnerError,
    ProjectNameNotNullError,
)
from app.schemas.projects import CreateProjectSchema, UpdateProjectSchema
from sqlalchemy import select


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


@pytest.mark.asyncio
async def test_create_project_200(async_session_maker, create_user_fix):
    async with async_session_maker() as session:
        service = ProjectService(ProjectRepository(session))
        data = CreateProjectSchema(**project_data_ok)
        user = (
            await session.scalars(select(UserModel).where(UserModel.id == 1))
        ).first()
        project = await service.create_project(data, user)

        assert project is not None
        assert project.title == project_data_ok["title"]
        assert project.description == project_data_ok["description"]


@pytest.mark.asyncio
async def test_create_project_409(async_session_maker, create_user_fix):
    async with async_session_maker() as session:
        service = ProjectService(ProjectRepository(session))
        data = CreateProjectSchema(**project_data_ok)
        user = (
            await session.scalars(select(UserModel).where(UserModel.id == 1))
        ).first()
        await service.create_project(data, user)
        with pytest.raises(ProjectNameExistingError):
            await service.create_project(data, user)


@pytest.mark.asyncio
async def test_update_project_200(async_session_maker, create_users_with_project):
    async with async_session_maker() as session:
        service = ProjectService(ProjectRepository(session))
        user = (
            await session.scalars(select(UserModel).where(UserModel.id == 1))
        ).first()
        update_data = UpdateProjectSchema(**project_data_update)
        updated_project = await service.update_project(update_data, user, 1)

        assert updated_project is not None
        assert updated_project.title == project_data_update["title"]
        assert updated_project.description == project_data_update["description"]


@pytest.mark.asyncio
async def test_update_project_404(async_session_maker, create_users_with_project):
    async with async_session_maker() as session:
        service = ProjectService(ProjectRepository(session))
        user = (
            await session.scalars(select(UserModel).where(UserModel.id == 1))
        ).first()
        update_data = UpdateProjectSchema(**project_data_update)

        with pytest.raises(ProjectNotFoundError):
            await service.update_project(update_data, user, 12)


@pytest.mark.asyncio
async def test_update_project_403(async_session_maker, create_users_with_project):
    async with async_session_maker() as session:
        service = ProjectService(ProjectRepository(session))
        user = (
            await session.scalars(select(UserModel).where(UserModel.id == 2))
        ).first()
        update_data = UpdateProjectSchema(**project_data_update)

        with pytest.raises(ProjectNotOwnerError):
            await service.update_project(update_data, user, 1)


@pytest.mark.asyncio
async def test_update_project_409(async_session_maker, create_users_with_project):
    async with async_session_maker() as session:
        service = ProjectService(ProjectRepository(session))
        user = (
            await session.scalars(select(UserModel).where(UserModel.id == 1))
        ).first()
        update_data = UpdateProjectSchema(**null_title_data_update)

        with pytest.raises(ProjectNameNotNullError):
            await service.update_project(update_data, user, 1)


@pytest.mark.asyncio
async def test_soft_delete_project_ok(async_session_maker, create_user_fix):
    async with async_session_maker() as session:
        repo = ProjectRepository(session)
        service = ProjectService(repo)

        project = await repo.create(project_data_ok)
        await session.commit()

        result = await service.soft_delete(
            project_id=project.id,
            user_id=project.owner_id,
        )

        await session.refresh(project)

        assert result == {"message": "Project status changed to inactive."}
        assert project.is_active is False


@pytest.mark.asyncio
async def test_soft_delete_project_not_found(async_session_maker):
    async with async_session_maker() as session:
        service = ProjectService(ProjectRepository(session))

        with pytest.raises(ProjectNotFoundError):
            await service.soft_delete(
                project_id=1,
                user_id=1,
            )


@pytest.mark.asyncio
async def test_soft_delete_project_not_owner(async_session_maker, create_user_fix):
    async with async_session_maker() as session:
        repo = ProjectRepository(session)
        service = ProjectService(repo)

        project = await repo.create(project_data_ok)
        await session.commit()

        with pytest.raises(ProjectNotOwnerError):
            await service.soft_delete(
                project_id=project.id,
                user_id=999,
            )


@pytest.mark.asyncio
async def test_hard_delete_project_ok(async_session_maker, create_user_fix):
    async with async_session_maker() as session:
        repo = ProjectRepository(session)
        service = ProjectService(repo)

        project = await repo.create(project_data_ok)
        await session.commit()

        result = await service.hard_delete(
            project_id=project.id,
            user_id=project.owner_id,
        )

        project_db = await repo.select_one(project.id)

        assert result == {"message": "Project was deleted."}
        assert project_db is None


@pytest.mark.asyncio
async def test_hard_delete_project_not_found(async_session_maker):
    async with async_session_maker() as session:
        service = ProjectService(ProjectRepository(session))

        with pytest.raises(ProjectNotFoundError):
            await service.hard_delete(
                project_id=1,
                user_id=1,
            )
