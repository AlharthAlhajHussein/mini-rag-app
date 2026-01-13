from .providers import OpenAIProvider, GeminiProvider, HuggingFaceProvider
from .llm_enums import LLMEnums


class LLMProviderFactory:
    
    def __init__(self, config: dict):
        self.config = config
        
    def create(self, provider_name: str):
        if provider_name == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                api_key= self.config.OPENAI_API_KEY,
                api_url= self.config.OPENAI_API_URL,
                default_input_max_characters= self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_output_max_characters= self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_temperature= self.config.GENERATION_DEFAULT_TEMPERATURE
                
            )
        if provider_name == LLMEnums.GEMINI.value:
            return GeminiProvider(
                api_key= self.config.GEMINI_API_KEY,
                default_input_max_characters= self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_output_max_characters= self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_temperature= self.config.GENERATION_DEFAULT_TEMPERATURE
            )
        if provider_name == LLMEnums.HUGGING_FACE.value:
            return HuggingFaceProvider(
                api_key= self.config.HUGGING_FACE_API_KEY,
                default_input_max_characters= self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_output_max_characters= self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_temperature= self.config.GENERATION_DEFAULT_TEMPERATURE
            )
        
        return None