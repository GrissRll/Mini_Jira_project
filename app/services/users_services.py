from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.schemas.users import CreateUserSchema, UserResponseSchema, UpdateUserSchema
from app.repositories.users import UserRepository
from app.models.users import User as UserModel
from sqlalchemy.exc import IntegrityError


async def create_user_services(db: AsyncSession, user: CreateUserSchema) -> UserModel:
    user_repo = UserRepository(db)
    filters = user_repo._build_or_filter(user.user_name, user.email)
    existing_user = await user_repo.get_user_on_filters(filters)
    if existing_user:
        if existing_user.user_name == user.user_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User name already existing")
        if existing_user.email == user.email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already existing")
    new_user = await user_repo.create(user)
    await db.commit()
    return new_user
