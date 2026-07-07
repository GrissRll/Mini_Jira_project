from sqlalchemy.ext.asyncio import AsyncSession
from app.models.projects import Project as ProjectModel
from app.models.users import User as UserModel
from app.models.tasks import Task as TaskModel
from sqlalchemy import select, update, Sequence, or_, and_, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.elements import ClauseElement, ColumnElement
from pydantic import EmailStr
from typing import List


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def build_filters(self,
                      owner_id: int | None = None,
                      project_id: int | None = None) -> List[ClauseElement | ColumnElement[bool]]:
        """
            Build a list of SQLAlchemy filter expressions for project queries.

            Return list of filter conditions.
        """
        filters = [ProjectModel.is_active == True]
        if owner_id is not None:
            filters.append(ProjectModel.owner_id == owner_id)
        if project_id is not None:
            filters.append(ProjectModel.id == project_id)
        return filters

    async def select_all_for_owner(self, owner_id: int) -> Sequence[ProjectModel]:
        """
            SELECT query for retrieving all active projects for owner.

            Return sequence of projects.
        """
        filters = self.build_filters(owner_id=owner_id)
        stmt = select(ProjectModel).where(*filters)
        res = (await self.db.scalars(stmt)).all()
        return res

    async def select_by_id(self, project_id: int) -> ProjectModel | None:
        """
            SELECT query for searching project by id.

            Return project or None.
        """
        filters = self.build_filters(project_id=project_id)
        stmt = select(ProjectModel).where(*filters)
        res = await self.db.scalar(stmt)
        return res

    async def select_all(self) -> Sequence[ProjectModel]:
        """
            SELECT query for retrieving all active projects.

            Return sequence of projects.
        """
        filters = self.build_filters()
        stmt = select(ProjectModel).where(*filters)
        res = (await self.db.scalars(stmt)).all()
        return res

    async def create(self, project_data: dict) -> ProjectModel:
        """
            INSERT query for creating new project.

            Return created project.
        """
        project = ProjectModel(**project_data)
        self.db.add(project)
        await self.db.flush()
        return project

    async def update(self, update_data: dict, project: ProjectModel) -> ProjectModel:
        """
            UPDATE query for modifying existing project.

            Return updated project.
        """
        for key, value in update_data.items():
            setattr(project, key, value)
        await self.db.flush()
        return project

    async def soft_delete(self, project_id: int) -> None:
        """
            UPDATE query for marking project as inactive.
        """
        stmt = update(ProjectModel).where(ProjectModel.id == project_id).values(is_active=False)
        await self.db.execute(stmt)
        await self.db.flush()

    async def hard_delete(self, project_id: int) -> None:
        """
            DELETE query for permanently removing project.
        """
        stmt = delete(ProjectModel).where(ProjectModel.id == project_id)
        await self.db.execute(stmt)
        await self.db.flush()
