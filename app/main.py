from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.api.routers.users_routers import router as users_router
from app.api.routers.projects_routers import router as projects_router
from app.api.routers.tasks_routers import router as tasks_router
from app.exceptions.registry import register_handlers

app = FastAPI()

register_handlers(app)

app.include_router(users_router)
app.include_router(projects_router)
app.include_router(tasks_router)

@app.get(path="/", response_class=JSONResponse)
async def index():
    return {"message": "start_app"}
