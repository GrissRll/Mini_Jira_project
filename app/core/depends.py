from .database import async_session_maker
from typing import AsyncGenerator
from app.repositories.users import UserRepository
from app.repositories.projects import ProjectRepository
from app.services.projects_service import ProjectService
from app.services.users_services import UserService
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.users import User as UserModel
from app.core.auth import hash_password, oauth2_scheme, verify_password
from app.core.config import ALGORITHM, SECRET_KEY
import jwt


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async generator for session object"""
    async with async_session_maker() as session:
        yield session


async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


async def get_user_service(user_repo: UserRepository = Depends(get_user_repository)):
    return UserService(user_repository=user_repo)


async def get_project_repository(
    db: AsyncSession = Depends(get_db),
) -> ProjectRepository:
    return ProjectRepository(db)


async def get_project_service(
    project_repo: ProjectRepository = Depends(get_project_repository),
) -> ProjectService:
    return ProjectService(project_repository=project_repo)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticated": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credential_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credential_exception
    result = await db.scalars(
        select(UserModel).where(UserModel.email == email, UserModel.is_active == True)
    )
    user = result.first()
    if user is None:
        raise credential_exception
    return user
