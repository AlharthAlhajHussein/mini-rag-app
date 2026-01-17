from enum import Enum

class LLMEnums(Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    HUGGING_FACE = "huggingface" 

class OpenAIEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    
class GeminiEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "model"  # Gemini uses 'model' instead of 'assistant'

    DOCUMENT = "retrieval_document"
    QUERY = "retrieval_query"

class HuggingFaceEnums(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class DocumentTypeEnums(Enum):
    DOCUMENT = "document"
    QUERY = "query"
