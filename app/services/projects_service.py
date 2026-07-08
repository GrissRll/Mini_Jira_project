from app.repositories.projects import ProjectRepository
from app.models.projects import Project as ProjectModel
from app.models.users import User as UserModel
from app.schemas.projects import CreateProjectSchema, UpdateProjectSchema
from typing import List
from app.exeptions.units.projects_exeptions import ProjectNotFoundError, ProjectNameExistingError
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
