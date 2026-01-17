import logging
from huggingface_hub import InferenceClient
from ..llm_interface import LLMInterface
from ..llm_enums import HuggingFaceEnums
class HuggingFaceProvider(LLMInterface):
    
    def __init__(self, api_key: str, 
                 default_input_max_characters: int = 1000,
                 default_output_max_characters: int = 1000,
                 default_temperature: float = 0.4):
        
        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_characters = default_output_max_characters
        self.default_temperature = default_temperature
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        
        # The InferenceClient can be used for text, images, and embeddings
        self.client = InferenceClient(token=self.api_key)
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_name: str) -> None:
        """Example model_name: 'meta-llama/Meta-Llama-3-8B-Instruct'"""
        self.generation_model_id = model_name

    def set_embedding_model(self, model_name: str, embedding_size: int = None) -> None:
        """Example model_name: 'sentence-transformers/all-MiniLM-L6-v2'"""
        self.embedding_model_id = model_name
        self.embedding_size = embedding_size

    def generate_text(self, prompt: str, chat_history: list = [], 
                      max_output_tokens: int = None, temperature: float = None) -> str:
        
        if not self.generation_model_id:
            self.logger.error("Hugging Face generation model ID is not set.")
            return None

        # Use the OpenAI-compatible chat completion method
        # This automatically handles the prompt formatting for most models
        chat_history.append(self.construct_prompt(prompt, role= HuggingFaceEnums.USER.value))

        try:
            response = self.client.chat_completion(
                model=self.generation_model_id,
                messages=chat_history,
                max_tokens=max_output_tokens or self.default_output_max_characters,
                temperature=temperature if temperature is not None else self.default_temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Hugging Face API error: {e}")
            return None

    def embed_text(self, text: str, document_type: str= None) -> list[float]:
        if not self.embedding_model_id:
            self.logger.error("Embedding model is not set.")
            return None

        try:
            # Get the raw vector from Hugging Face
            vector = self.client.feature_extraction(text, model=self.embedding_model_id)
            
            # Convert to list
            embedding_list = vector.tolist()

            # --- AUTO-DETECTION LOGIC ---
            # If we don't know the size yet, let's learn it from the first result!
            if self.embedding_size is None:
                self.embedding_size = len(embedding_list)
                self.logger.info(f"Auto-detected embedding size for {self.embedding_model_id}: {self.embedding_size}")
            
            return embedding_list
        
        except Exception as e:
            self.logger.error(f"HF Embedding error: {e}")
            return None

    def construct_prompt(self, prompt, role):
        return {"role": role, "content": self.process_text(prompt)}
    
    def process_text(self, text: str) -> str:
        return text[:self.default_input_max_characters].strip()
    