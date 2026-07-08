from app.repositories.projects import ProjectRepository
from app.models.projects import Project as ProjectModel
from app.models.users import User as UserModel
from app.schemas.projects import CreateProjectSchema, UpdateProjectSchema
from typing import List
from app.exeptions.units.projects_exeptions import ProjectNotFoundError, ProjectNameExistingError, ProjectNotOwnerError, \
    ProjectNameNotNullError
from sqlalchemy.exc import IntegrityError


class ProjectService:
    def __init__(self, project_repository: ProjectRepository):
        self.project_repo = project_repository

    async def get_projects(self) -> List[ProjectModel]:
        projects = await self.project_repo.select_many()
        return projects

    async def get_project(self, project_id: int) -> ProjectModel:
        project = await self.project_repo.select_one(project_id)
        if project is None:
            raise ProjectNotFoundError()
        return project

    async def get_owner_projects(self, owner_id: int) -> List[ProjectModel]:
        projects = await self.project_repo.select_many(owner_id)
        if not projects:
            raise ProjectNotFoundError()
        return projects

    async def create_project(self, project_data: CreateProjectSchema, user: UserModel) -> ProjectModel:
        project_existing = await self.project_repo.select_one(title=project_data.title)
        if project_existing:
            raise ProjectNameExistingError()
        project_data = project_data.model_dump()
        project_data["owner_id"] = user.id
        try:
            project = await self.project_repo.create(project_data)
            await self.project_repo.db.commit()
            return project
        except IntegrityError as exc:
            await self.project_repo.db.rollback()
            raise ProjectNameExistingError()

    async def update_project(self, updated_data: UpdateProjectSchema, user: UserModel, project_id: int):
        existing_project = await self.project_repo.select_one(project_id=project_id)
        if not existing_project:
            raise ProjectNotFoundError()
        if existing_project.owner_id != user.id:
            raise ProjectNotOwnerError()
        updated_data = updated_data.model_dump(exclude_unset=True)
        for key in updated_data:
            if updated_data[key] is None and key == "title":
                raise ProjectNameNotNullError()
        try:
            updated_project = await self.project_repo.update(updated_data)
            await self.project_repo.db.commit()
            return updated_project
        except IntegrityError as exc:
            await self.project_repo.db.rollback()
            errors = str(exc.orig)
            if "un_projects_title" in errors:
                raise ProjectNameExistingError()
        raise
