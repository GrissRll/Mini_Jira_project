from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.core.database import create_engine, create_async_session
from app.api.routers.users_routers import router as users_router
from app.api.routers.projects_routers import router as projects_router
from app.api.routers.tasks_routers import router as tasks_router
from app.exceptions.registry import register_handlers
from typing import AsyncIterator

@asynccontextmanager
async def lifespan(application:FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    engine = create_engine(settings.database_url)
    async_session = create_async_session(engine)

    application.state.async_session = async_session
    application.state.settings = settings

    try:
        yield
    finally:
        await engine.dispose()

def create_application() -> FastAPI:
    application = FastAPI(
        title="Mini_jira",
        lifespan=lifespan,
    )

    register_handlers(application)

    application.include_router(users_router)
    application.include_router(projects_router)
    application.include_router(tasks_router)


    @application.get(path="/", response_class=JSONResponse)
    async def index():
        return {"message": "start_app"}

    return application

app = create_application()
