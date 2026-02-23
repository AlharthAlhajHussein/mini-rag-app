from fastapi import FastAPI
from routes import base, data, nlp
from helpers import get_settings
from stores.llm import LLMProviderFactory
from stores.vector_db import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from utils.metrics import setup_metrics


app = FastAPI()

# setup Prometheus metrics
setup_metrics(app)

@app.on_event("startup")
async def startup():
    settings = get_settings()
    
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRESQL_USERNAME}:{settings.POSTGRESQL_PASSWORD}@{settings.POSTGRESQL_HOST}:{settings.POSTGRESQL_PORT}/{settings.POSTGRESQL_MAIN_DB}"
    app.postgres_engine = create_async_engine(postgres_conn)
    app.db_client = sessionmaker(app.postgres_engine, class_=AsyncSession, expire_on_commit=False)
    print("Connected to the PostgreSQL database!")
    
    llm_provider_factory = LLMProviderFactory(config=settings)
    vector_db_provider_factory = VectorDBProviderFactory(config=settings, db_client=app.db_client)

    # Generation Client
    app.generation_client = llm_provider_factory.create(provider_name=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)
    
    # Embedding Client
    app.embedding_client = llm_provider_factory.create(provider_name=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_SIZE)
    
    # Vector DB Client
    app.vector_db_client = vector_db_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    await app.vector_db_client.connect()
    
    app.template_parser = TemplateParser(language=settings.PRIMARY_LANGUAGE, default_language=settings.DEFAULT_LANGUAGE)
    
    
    
@app.on_event("shutdown")
async def shutdown():
    await app.postgres_engine.dispose()
    print("Disconnected from the PostgreSQL database!")
    await app.vector_db_client.disconnect()

# app.router.lifespan.on_startup.append(startup_span)
# app.router.lifespan.on_shutdown.append(shutdown_span)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
