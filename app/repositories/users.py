from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import User as UserModel
from sqlalchemy import select, Sequence, or_, and_
from app.schemas.users import CreateUserSchema
from sqlalchemy.sql.elements import ClauseElement, BooleanClauseList, ColumnElement
from pydantic import EmailStr


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> Sequence[UserModel]:
        """
            SELECT query for getting all users
        """
        stmt = select(UserModel)
        return (await self.db.scalars(stmt)).all()

    async def create(self, user_data: CreateUserSchema) -> UserModel:
        """
            INSERT query for add new user in db
        """
        new_user = UserModel(**user_data.model_dump())
        self.db.add(new_user)
        await self.db.flush()
        await self.db.refresh(new_user)
        return new_user

    async def get_user_on_filters(self, filters: ColumnElement) -> UserModel | None:
        """"
            SELECT query for searching user on filters list.
            Return user or None
        """
        stmt = select(UserModel).where(filters)
        result = (await self.db.scalars(stmt)).first()
        return result

    def _buid_and_filter(self, user_name: str | None,
                         email: EmailStr | None) -> ClauseElement | None | ColumnElement[bool]:
        filters = []
        if user_name:
            filters.append(UserModel.user_name == user_name)
        if email:
            filters.append(UserModel.email == email)
        if not filters:
            return None
        return and_(*filters)

    def _build_or_filter(self, user_name: str | None,
                         email: EmailStr | None) -> ClauseElement | None | ColumnElement[bool]:
        filters = []
        if user_name:
            filters.append(UserModel.user_name == user_name)
        if email:
            filters.append(UserModel.email == email)

        if not filters:
            return None
        return or_(*filters)
