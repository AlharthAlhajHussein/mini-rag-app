from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from routes import base, data
from helpers import get_settings
from stores.llm import LLMProviderFactory


app = FastAPI()

# @app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URI)
    app.database = app.mongodb_client[settings.MONGODB_DB_NAME]
    print("Connected to the MongoDB database!")
    
    llm_provider_factory = LLMProviderFactory(config=settings)

    # Generation Client
    app.generation_client = llm_provider_factory.create(provider_name=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)
    
    # Embedding Client
    app.embedding_client = llm_provider_factory.create(provider_name=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_SIZE)
    
# @app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
    print("Disconnected from the MongoDB database!")

app.router.lifespan.on_startup.append(startup_db_client)
app.router.lifespan.on_shutdown.append(shutdown_db_client)

app.include_router(base.base_router)
app.include_router(data.data_router)
