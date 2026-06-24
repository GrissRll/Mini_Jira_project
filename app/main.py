from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get(path="/", response_class=JSONResponse)
async def index():
    return {"message": "start_app"}
