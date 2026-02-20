import logging
from ..llm_interface import LLMInterface
from ..llm_enums import GeminiEnums, DocumentTypeEnums
# import google.generativeai as genai
from google import genai
from google.genai import types
from typing import Union, List

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
        self.client = genai.Client(api_key=self.api_key)
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

        
        # Extract system instruction from chat history (Gemini doesn't support 'system' role in messages)
        system_instruction = None
        filtered_history = []
                
        for message in chat_history:
            if message.get("role") == "system":
                # Use the first system message as system_instruction
                if system_instruction is None and message.get("parts"):
                    part = message["parts"][0]
                    # Check if 'part' is a dict or an object and get the text
                    if isinstance(part, dict):
                        system_instruction = part.get("text")
                    else:
                        system_instruction = getattr(part, 'text', str(part))
            else:
                # Keep only user and model messages
                filtered_history.append(message)

        # Construct the new user message
        user_message = self.construct_prompt(prompt=prompt, role=GeminiEnums.USER.value)
        messages = filtered_history + [user_message]
        
        # print(f"Messages sent to Gemini: {messages}")
        max_output_tokens = max_output_tokens or self.default_output_max_characters
        
        response = self.client.models.generate_content(
            model=self.generation_model_id,
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=max_output_tokens,
                temperature=temperature if temperature is not None else self.default_temperature
            ),
        )
            
        if not response or not response.text:
            # Handle cases where finish_reason is MAX_TOKENS but text is partial
            if response and response.candidates[0].finish_reason == "MAX_TOKENS":
                self.logger.warning("Response was truncated due to token limits.")
                # Still return whatever text was generated before the cutoff
                return response.text.strip() if response.text else "The answer was too long to display."
            self.logger.error("Failed to get text from Gemini response.")
            return None
        answer = response.text        
        
        return answer
    
    def construct_prompt(self, prompt: str, role: str) -> dict:
        """
        Returns a plain dictionary instead of using types.Part.from_text directly.
        The Gemini SDK accepts plain dictionaries, and these ARE JSON serializable.
        """
        return {
            "role": role,
            "parts": [{"text": prompt}] # Use a plain dict here instead of types.Part
        }

    def process_text(self, text: str) -> str:
        return text[:self.default_input_max_characters].strip()

    def embed_text(self, text: Union[str, List[str]], document_type: str = None) -> list[float]:
        if not self.embedding_model_id:
            self.logger.error("Embedding model is not set.")
            return None
        
        if isinstance(text, str):
            text = [text]
        
        # Mapping your internal document types to Gemini-specific task types
        input_type = GeminiEnums.DOCUMENT.value
        if document_type == DocumentTypeEnums.QUERY.value:
            input_type = GeminiEnums.QUERY.value
        
        try:
            embed_config = {
                "task_type": input_type,
                "output_dimensionality": self.embedding_size
            }
            # We pass output_dimensionality to the API. 
            # Note: This only works with newer models like 'text-embedding-004'
            result = self.client.models.embed_content(
                model=self.embedding_model_id,
                contents=[self.process_text(t) for t in text],
                config=embed_config
            )
            
            # 1. Check for the attribute instead of the dictionary key
            if not result or not hasattr(result, 'embeddings'):
                self.logger.error("No embeddings attribute found in result")
                return None

            # 2. Extract the values from each ContentEmbedding object
            # Each 'ContentEmbedding' has a 'values' attribute which is the list of floats
            embeddings_list = [item.values for item in result.embeddings]

            # 3. Return the result
            return embeddings_list
                            
        except Exception as e:
            self.logger.error(f"Gemini embedding error: {str(e)}")
            return None
        
    