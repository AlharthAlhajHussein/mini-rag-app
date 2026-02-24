APP_NAME="Mini RAG Application"
APP_VERSION="0.1.0"


FILE_ALLOWED_TYPES=["text/plain", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
FILE_MAX_SIZE=100
FILE_DEFAULT_CHUNK_SIZE=512000  # 512KB


POSTGRESQL_USERNAME=
POSTGRESQL_PASSWORD=
POSTGRESQL_HOST=
POSTGRESQL_PORT=
POSTGRESQL_MAIN_DB = 

#=================================== LLM Configurations ===================================#

GENERATION_BACKEND="gemini"  # Options: openai, gemini, huggingface, ollama
EMBEDDING_BACKEND="gemini"   # Options: openai, gemini, huggingface, ollama


OPENAI_API_KEY=
GEMINI_API_KEY=
HUGGING_FACE_API_KEY= 
OLLAMA_API_KEY=
OLLAMA_HOST="http://192.168.1.109:11434"  # local Ollama host 
# OLLAMA_HOST="https://ollama.com" # remote Ollama host if using cloud models

GENERATION_MODEL_ID = "gemini-2.5-flash"  # OpenAI: gpt-4o | Gemini: gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite | HuggingFace: Qwen/Qwen2.5-3B-Instruct | ollama: , gemma3:1b, gemma3:12b-cloud
EMBEDDING_MODEL_ID = "gemini-embedding-001"  # OpenAI: text-embedding-3-small | Gemini: models/gemini-embedding-001, models/gemini-embedding-004 | HuggingFace: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | ollama: nomic-embed-text:137m-v1.5-fp16, embeddinggemma:300m-bf16, qwen3-embedding:4b-q8_0 
EMBEDDING_SIZE=768  # OpenAI: 3076,1536 | Gemini: 768 | HuggingFace: 384 | Ollama: 384, 768


INPUT_DEFAULT_MAX_CHARACTERS=2000
GENERATION_DEFAULT_MAX_TOKENS=2000
GENERATION_DEFAULT_TEMPERATURE=0.2

#=================================== Vector DB Configurations ===================================#

VECTOR_DB_BACKEND="pgvector"  # Options: qdrant_db, pgvector
VECTOR_DB_PATH="qdrant_db"
VECTOR_DB_DISTANCE_METRIC="cosine"  # Options: Cosine, Euclidean, DotProduct
VECTOR_DB_PGVEC_INDEX_THRESHOLD=10000  # Threshold for apply indexing strategy in pgvector provider, if number of vectors in collection exceeds this threshold, it will create an index on the vector column for faster similarity search
#=================================== Template Configurations ===================================#
PRIMARY_LANGUAGE = "ar"
DEFAULT_LANGUAGE = "en"
