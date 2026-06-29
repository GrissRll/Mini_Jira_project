from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.api.routers.users_routers import router as users_router

app = FastAPI()

app.include_router(users_router)


@app.get(path="/", response_class=JSONResponse)
async def index():
    return {"message": "start_app"}
