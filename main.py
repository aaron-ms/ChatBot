from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes.chat_routes import router


app = FastAPI()
app.include_router(router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Running!"}