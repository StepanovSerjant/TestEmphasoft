from fastapi import FastAPI

from core.db import database
from users.routes import users_router


app = FastAPI()
app.include_router(users_router, prefix="/users", tags=["users"])


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

