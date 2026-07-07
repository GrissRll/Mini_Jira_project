from app.repositories.projects import ProjectRepository
from app.models.projects import Project as ProjectModel
from app.models.users import User as UserModel
from app.schemas.projects import CreateProjectSchema
from typing import List
from app.exeptions.units.projects_exeptions import ProjectNotFoundError


class ProjectService:
    def __init__(self, project_repository: ProjectRepository):
        self.project_repo = project_repository

    async def get_projects(self) -> List[ProjectModel]:
        projects = await self.project_repo.select_all()
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