from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME: str = "Mini RAG App"
    APP_VERSION: str = "0.1.0"

    FILE_ALLOWED_TYPES: list = ["text/plain", "application/pdf"] # Allowed MIME types for file uploads
    FILE_MAX_SIZE: int = 10  # in MB
    FILE_DEFAULT_CHUNK_SIZE: int = 512000  # 512KB
    
    
    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_MAIN_DB: str
    POSTGRESQL_HOST: str = "localhost"
    POSTGRESQL_PORT: int = 5432
    ADDITIONAL_GCP: str = ""  # Additional connection parameters for GCP Cloud SQL

    GENERATION_BACKEND: str = "gemini"  # Options: openai, gemini, huggingface
    EMBEDDING_BACKEND: str = "gemini"   # Options: openai, gemini, huggingface


    OPENAI_API_KEY: str = None
    GEMINI_API_KEY: str = None
    HUGGING_FACE_API_KEY: str = None
    OLLAMA_API_KEY: str = None
    OLLAMA_HOST: str = None
    
    GENERATION_MODEL_ID: str = "gemini-2.5-flash"  # OpenAI: gpt-4o, gpt-3.5-turbo | Gemini: gemini-1.5-pro | HuggingFace: meta-llama/Llama-2-7b-chat-hf
    EMBEDDING_MODEL_ID: str = "gemini-embedding-001"  # OpenAI: text-embedding-3-small | Gemini: models/text-embedding-004 | HuggingFace: sentence-transformers/all-MiniLM-L6-v2
    EMBEDDING_SIZE: int = 768  # OpenAI: 3076,1536 | Gemini: 768 | HuggingFace: 384

    INPUT_DEFAULT_MAX_CHARACTERS: int = 2000
    GENERATION_DEFAULT_MAX_TOKENS: int = 2000
    GENERATION_DEFAULT_TEMPERATURE: float = 0.2
    
    VECTOR_DB_BACKEND: str= "pgvector"  # Options: qdrant_db, pinecone_db, weaviate_db, faiss_db
    VECTOR_DB_PATH: str= "qdrant_db"  # For qdrant_db, this is the path where the qdrant server will store its data. For pgvector, this is not used.
    VECTOR_DB_DISTANCE_METRIC: str = "cosine"  # Options: Cosine, Euclidean, DotProduct
    VECTOR_DB_PGVEC_INDEX_THRESHOLD: int = 8000  # Threshold for apply indexing strategy in pgvector provider, if number of vectors in collection exceeds this threshold, it will create an index on the vector column for faster similarity search
    
    PRIMARY_LANGUAGE: str = 'en'
    DEFAULT_LANGUAGE: str = 'en'
    
    model_config = SettingsConfigDict(env_file=".env")
        
def get_settings():
    return Settings()
    

