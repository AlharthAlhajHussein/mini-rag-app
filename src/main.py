from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from routes import base, data, nlp
from helpers import get_settings
from stores.llm import LLMProviderFactory
from stores.vector_db import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser

app = FastAPI()

@app.on_event("startup")
async def startup():
    settings = get_settings()
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URI)
    app.database = app.mongodb_client[settings.MONGODB_DB_NAME]
    print("Connected to the MongoDB database!")
    
    llm_provider_factory = LLMProviderFactory(config=settings)
    vector_db_provider_factory = VectorDBProviderFactory(config=settings)

    # Generation Client
    app.generation_client = llm_provider_factory.create(provider_name=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)
    
    # Embedding Client
    app.embedding_client = llm_provider_factory.create(provider_name=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_SIZE)
    
    # Vector DB Client
    app.vector_db_client = vector_db_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vector_db_client.connect()
    
    app.template_parser = TemplateParser(language=settings.PRIMARY_LANGUAGE, default_language=settings.DEFAULT_LANGUAGE)
    
    
    
@app.on_event("shutdown")
async def shutdown():
    app.mongodb_client.close()
    print("Disconnected from the MongoDB database!")
    app.vector_db_client.disconnect()

# app.router.lifespan.on_startup.append(startup_span)
# app.router.lifespan.on_shutdown.append(shutdown_span)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
