from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import User as UserModel
from sqlalchemy import select, Sequence
from app.schemas.users import CreateUserSchema


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
