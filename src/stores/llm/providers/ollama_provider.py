from ..llm_interface import LLMInterface
from ..llm_enums import OllamaEnums
import ollama
import logging


class OllamaProvider(LLMInterface):
    
    def __init__(self, api_key: str,
                 default_input_max_characters: int= 1000,
                 default_output_max_characters: int= 1000,
                 default_temperature: float = 0.1):
        
        
        self.api_key = api_key
        
        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_characters = default_output_max_characters
        self.default_temperature = default_temperature
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = None
        self.enums = OllamaEnums
        self.logger = logging.getLogger(__name__)
        
    def set_generation_model(self, model_name: str) -> None:
        self.generation_model_id = model_name

    def set_embedding_model(self, model_name: str, embedding_size: int = None) -> None:
        self.embedding_model_id = model_name
        self.embedding_size = embedding_size
        
    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None, temperature: float = None) -> str:

        
        # if not self.client:
        #     logging.error("OpenAI client is not initialized.")
        #     return None
            
        if not self.generation_model_id:
            logging.error("Generation model from Ollama provider is not set.")
            return None
        
        max_tokens = max_output_tokens if max_output_tokens is not None else self.default_output_max_characters
        temp = temperature if temperature is not None else self.default_temperature

        chat_history.append(self.construct_prompt(prompt, role=OllamaEnums.USER.value))
        
        try:
            response = ollama.chat(
                model=self.generation_model_id,
                messages=chat_history,
                options={
                    "num_predict":max_tokens,
                    "temperature":temp
                }
            )
        except Exception as e:
            logging.error(f"Failed to get response from Ollama {self.generation_model_id} model: {e}")
            return None
        
        if response is None:
            logging.error(f"Failed to get response from Ollama {self.generation_model_id} model.")
            return None 
        
        return response.message.content
    
    def construct_prompt(self, prompt: str, role: str) -> dict:
        return {"role": role,
                "content": self.process_text(prompt)}

    def process_text(self, text: str) -> str:
        return text[:self.default_input_max_characters].strip()
    
    def embed_text(self, text: str, document_type: str = None) -> list[float]:
        if not self.embedding_model_id:
            self.logger.error("Embedding model is not set.")
            return None

        # if document_type:
        #     text = document_type + ": " + text
        
        # Build the arguments for the API call
        params = {
            "input": text,
            "model": self.embedding_model_id
        }

        # If self.embedding_size is set, we pass it to shorten the vector.
        if self.embedding_size:
            params["dimensions"] = self.embedding_size

        try:
            
            response = ollama.embed(**params)
            
            if not response or 'embeddings' not in response or not response['embeddings']:
                return None
            
            vector = response['embeddings'][0]
            
            # AUTO-DETECTION: Update embedding_size if it was previously unknown
            if self.embedding_size is None:
                self.embedding_size = len(vector)
                self.logger.info(f"Auto-detected Ollama {self.embedding_model_id} embedding size: {self.embedding_size}")
            
            return vector
        
        except Exception as e:
            self.logger.error(f"Ollama embedding error: {e}")
            return None
    
