import logging
# from google import genai
# from google.genai import types
from ..llm_interface import LLMInterface
from ..llm_enums import GeminiEnums, DocumentTypeEnums
import google.generativeai as genai

class GeminiProvider(LLMInterface):
    
    def __init__(self, api_key: str, 
                 default_input_max_characters: int = 1000,
                 default_output_max_characters: int = 1000,
                 default_temperature: float = 0.1):
        
        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_characters = default_output_max_characters
        self.default_temperature = default_temperature
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        # Initialize the Google Generative AI client
        genai.configure(api_key=self.api_key)
        self.client = None  # Not needed, use genai directly
        self.enums = GeminiEnums
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_name: str) -> None:
        self.generation_model_id = model_name

    def set_embedding_model(self, model_name: str, embedding_size: int = None) -> None:
        self.embedding_model_id = model_name
        self.embedding_size = embedding_size

    def generate_text(self, prompt: str, chat_history: list = [], 
                      max_output_tokens: int = None, temperature: float = None) -> str:
            
        if not self.generation_model_id:
            self.logger.error("Generation model for Gemini provider is not set.")
            return None

        # Gemini uses 'max_output_tokens' and 'temperature' inside a config object
        config = genai.types.GenerationConfig(
            max_output_tokens=max_output_tokens or self.default_output_max_characters,
            temperature=temperature if temperature is not None else self.default_temperature
        )

        model = genai.GenerativeModel(self.generation_model_id)
        
        # For Gemini, the 'contents' argument handles the conversation history
        # If history exists, we append the current message to it
        messages = chat_history + [self.construct_prompt(prompt=prompt, role=GeminiEnums.USER.value)]
        
        response = model.generate_content(
            messages,
            generation_config=config
        )
            
        if not response or not response.text:
            self.logger.error("Failed to get text from Gemini response.")
            return None
            
        return response.text
            


    def embed_text(self, text: str, document_type: str = None) -> list[float]:
        if not self.embedding_model_id:
            self.logger.error("Embedding model is not set.")
            return None

        # Mapping your internal document types to Gemini-specific task types
        input_type = GeminiEnums.DOCUMENT.value
        if document_type == DocumentTypeEnums.QUERY.value:
            input_type = GeminiEnums.QUERY.value
        
        try:
            # We pass output_dimensionality to the API. 
            # Note: This only works with newer models like 'text-embedding-004'
            result = genai.embed_content(
                model=self.embedding_model_id,
                content=text,
                task_type=input_type,
                output_dimensionality=self.embedding_size # <--- Added this line
            )
            
            # In the google-generativeai library, the response is typically 
            # accessed via result['embedding']
            if not result or 'embedding' not in result:
                return None
            
            vector = result['embedding']
            
            # AUTO-DETECTION: Update self.embedding_size if it was unknown
            if self.embedding_size is None:
                self.embedding_size = len(vector)
                self.logger.info(f"Auto-detected Gemini embedding size: {self.embedding_size}")
                
            return vector
                            
        except Exception as e:
            self.logger.error(f"Gemini embedding error: {str(e)}")
            return None

    def construct_prompt(self, prompt: str, role: str) -> dict:
        """
        Gemini-compliant role mapping: 'user' or 'model'.
        """
        return {
            "role": role,
            "parts": [{"text": self.process_text(prompt)}]
        }

    def process_text(self, text: str) -> str:
        return text[:self.default_input_max_characters].strip()
    