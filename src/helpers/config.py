from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    API_KEY: str

    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int
    
    # MONGODB_URI: str
    # MONGODB_DB_NAME: str
    
    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_MAIN_DB: str
    POSTGRESQL_HOST: str = "localhost"
    POSTGRESQL_PORT: int = 5432
     

    GENERATION_BACKEND: str  # Options: openai, gemini, huggingface
    EMBEDDING_BACKEND: str   # Options: openai, gemini, huggingface


    OPENAI_API_KEY: str = None
    GEMINI_API_KEY: str = None
    HUGGING_FACE_API_KEY: str = None
    OLLAMA_API_KEY: str = None
    OLLAMA_HOST: str = None
    
    GENERATION_MODEL_ID: str = None  # OpenAI: gpt-4o, gpt-3.5-turbo | Gemini: gemini-1.5-pro | HuggingFace: meta-llama/Llama-2-7b-chat-hf
    EMBEDDING_MODEL_ID: str = None  # OpenAI: text-embedding-3-small | Gemini: models/text-embedding-004 | HuggingFace: sentence-transformers/all-MiniLM-L6-v2
    EMBEDDING_SIZE: int = None  # OpenAI: 3076,1536 | Gemini: 768 | HuggingFace: 384

    INPUT_DEFAULT_MAX_CHARACTERS: int = None
    GENERATION_DEFAULT_MAX_TOKENS: int = None
    GENERATION_DEFAULT_TEMPERATURE: float = None
    
    VECTOR_DB_BACKEND: str  # Options: qdrant_db, pinecone_db, weaviate_db, faiss_db
    VECTOR_DB_PATH: str
    VECTOR_DB_DISTANCE_METRIC: str = None  # Options: Cosine, Euclidean, DotProduct
    
    PRIMARY_LANGUAGE: str = 'en'
    DEFAULT_LANGUAGE: str = 'en'
    
    model_config = SettingsConfigDict(env_file=".env")
        
def get_settings():
    return Settings()
    

