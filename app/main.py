from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.api.routers.users_routers import router as users_router
from core.exeption_handlers import register_exception_handler

app = FastAPI()

register_exception_handler(app)

app.include_router(users_router)


@app.get(path="/", response_class=JSONResponse)
async def index():
    return {"message": "start_app"}
