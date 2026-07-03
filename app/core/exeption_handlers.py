from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse

from app.exeptions.users_exeptions import (
    UserAlreadyExistsError,
    UserEmailAlreadyExistsError,
    UserForbiddenError,
    UserNameAlreadyExistsError,
    UserNotFoundError,
    UserInvalidData,
    UserAuthorizationError
)


def register_exception_handler(app: FastAPI):
    @app.exception_handler(UserAlreadyExistsError)
    async def user_exist_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "User already existing"}
        )

    @app.exception_handler(UserNameAlreadyExistsError)
    async def user_name_exist_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "User name already existing"}
        )

    @app.exception_handler(UserEmailAlreadyExistsError)
    async def user_email_exist_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "User email already existing"}
        )

    @app.exception_handler(UserNotFoundError)
    async def user_not_foud_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "User not found"}
        )

    @app.exception_handler(UserForbiddenError)
    async def user_owner_handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Only owner can update or delete profile"}
        )

    @app.exception_handler(UserInvalidData)
    async def user_owner_handler(request: Request, exc: UserInvalidData):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exc}
        )

    @app.exception_handler(UserAuthorizationError)
    async def user_owner_handler(request: Request, exc: UserAuthorizationError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Incorrect email or password"},
            headers={"WWW-Authenticate": "Bearer"}
        )
