from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from routes import base, data
from helpers import get_settings

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URI)
    app.database = app.mongodb_client[settings.MONGODB_DB_NAME]
    print("Connected to the MongoDB database!")

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
    print("Disconnected from the MongoDB database!")

app.include_router(base.base_router)
app.include_router(data.data_router)
