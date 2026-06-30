from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import User as UserModel
from sqlalchemy import select, update, Sequence, or_, and_, delete
from app.schemas.users import CreateUserSchema, UpdateUserSchema
from sqlalchemy.sql.elements import ClauseElement, ColumnElement
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

    async def get_users_on_filters(self, filters: ColumnElement, page_num: int, page_size: int) -> Sequence[UserModel]:
        """"
            SELECT query for searching USERS on filters list.
            Return USERS LIST
        """

        stmt = (select(UserModel).
                where(filters).
                order_by(UserModel.id).
                offset((page_num - 1) * page_size).
                limit(page_size))
        result = (await self.db.scalars(stmt)).all()
        return result

    def _buid_and_filter(self, user_name: str | None = None,
                         email: EmailStr | None = None,
                         user_id: int | None = None) -> ClauseElement | None | ColumnElement[bool]:
        filters = [UserModel.is_active == True]
        if user_name:
            filters.append(UserModel.user_name == user_name)
        if email:
            filters.append(UserModel.email == email)
        if user_id:
            filters.append(UserModel.id == user_id)
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
        return and_(UserModel.is_active == True, or_(*filters))

    async def update(self, user: UserModel, user_data: dict) -> UserModel:
        for key, value in user_data.items():
            setattr(user, key, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def soft_delete(self, user_id: int):
        stmt = update(UserModel).where(UserModel.id == user_id).values(is_active=False)
        await self.db.execute(stmt)
        await self.db.flush()

    async def hard_delete(self, user_id: int):
        stmt = delete(UserModel).where(UserModel.id == user_id)
        await self.db.execute(stmt)
        await self.db.flush()
