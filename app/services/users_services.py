from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.schemas.users import CreateUserSchema, UserResponseSchema, UpdateUserSchema
from app.repositories.users import UserRepository
from app.models.users import User as UserModel
from sqlalchemy.exc import SQLAlchemyError



class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository




async def create_user_services(db: AsyncSession, user: CreateUserSchema) -> UserModel:
    user_repo = UserRepository(db)
    filters = user_repo._build_or_filter(user.user_name, user.email)
    existing_user = await user_repo.get_user_on_filters(filters)
    if existing_user.user_name == user.user_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User name already existing")
    if existing_user.email == user.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already existing")
    new_user = await user_repo.create(user)
    await db.commit()
    return new_user


async def get_all_users_service(db: AsyncSession,

                                page_num: int = 1,
                                page_size: int = 10, ) -> list[UserModel]:
    user_repo = UserRepository(db)
    filters = user_repo._buid_and_filter()
    users = await user_repo.get_users_on_filters(filters, page_num, page_size)
    return users


async def get_user_by_id_service(db: AsyncSession, user_id: int) -> UserModel:
    user_repo = UserRepository(db)
    filters = user_repo._buid_and_filter(user_id=user_id)
    existing_user = await user_repo.get_user_on_filters(filters)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return existing_user


async def update_user_service(db: AsyncSession, updated_data: UpdateUserSchema, user: UserModel,
                              user_id: int) -> UserModel:
    if user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can update profile")

    updated_data = updated_data.model_dump(exclude_unset=True)
    for key in updated_data:
        if updated_data[key] is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=f"{key} cannot be null")
    user_repo = UserRepository(db)
    try:
        user = await user_repo.update(user, updated_data)
        await db.commit()
        return user
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Operation was cancelled due to current state conflict")

