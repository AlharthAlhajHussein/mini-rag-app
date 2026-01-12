from stores.llm_interface import LLMInterface
from stores.llm_enums import OpenAIEnums
from openai import OpenAI
import logging


class OpenAIProvider(LLMInterface):
    
    def __init__(self, api_key: str, api_url: str = None,
                 default_input_max_charcters: int= 1000,
                 default_output_max_charcters: int= 1000,
                 default_temperature: float = 0.1):
        
        self.api_key = api_key
        self.api_url = api_url
        
        self.default_input_max_charcters = default_input_max_charcters
        self.default_output_max_charcters = default_output_max_charcters
        self.default_temperature = default_temperature
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(api_key=self.api_key, api_base=self.api_url)
        self.logger = logging.getLogger(__name__)
        
    
    def set_generation_model(self, model_name: str) -> None:
        self.generation_model_id = model_name

    def set_embedding_model(self, model_name: str, embedding_size: int = None) -> None:
        self.embedding_model_id = model_name
        self.embedding_size = embedding_size


    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None, temperature: float = None) -> str:

        
        if not self.client:
            logging.error("OpenAI client is not initialized.")
            return None
            
        if not self.generation_model_id:
            logging.error("Generation model from OpenAI provider is not set.")
            return None
        
        max_tokens = max_output_tokens if max_output_tokens is not None else self.default_output_max_charcters
        temp = temperature if temperature is not None else self.default_temperature

        chat_history.append(self.construct_prompt(prompt, role=OpenAIEnums.USER.value))
        
        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_tokens,
            temperature=temp
        )
        
        if response is None or 'choices' not in response or len(response.choices) == 0 or not response.choices[0].message.content:
            logging.error("Failed to get response from OpenAI.")
            return None
        
        return response.choices[0].message['content']

    
    def embed_text(self, text: str, document_type: str = None) -> list[float]:
       
        if not self.client:
            logging.error("OpenAI client is not initialized.")
            return None
            
        if not self.embedding_model_id:
            logging.error("Embedding model is not set.")
            return None

        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model_id
        )

        if response is None or 'data' not in response or len(response.data) == 0 or not response.data[0].embedding:
            logging.error("Failed to get embedding from OpenAI.")
            return None
        
        return response.data[0].embedding   


    def construct_prompt(self, prompt: str, role: str) -> dict:
        return {"role": role,
                "content": self.process_text(prompt)}

    def process_text(self, text: str) -> str:
        return text[:self.default_input_max_charcters].strip()