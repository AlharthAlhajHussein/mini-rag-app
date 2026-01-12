from abc import ABC, abstractmethod


class LLMInterface(ABC):

    @abstractmethod
    def set_generation_model(self, model_name: str) -> None:
        """Set the language model to be used for text generation."""
        pass
    
    @abstractmethod
    def set_embedding_model(self, model_name: str) -> None:
        """Set the embedding model to be used for text embedding."""
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str, chat_history: list = [], max_output_tokens: int = None, temperature: float = None) -> str:
        """Generate text based on the given prompt."""
        pass
    
    @abstractmethod
    def embed_text(self, text: str, document_type: str = None) -> list[float]:
        """Generate an embedding for the given text."""
        pass
    
    @abstractmethod
    def construct_prompt(self, prompt: str, role: str) -> str:
        """Construct a prompt by filling in the template with the provided variables."""
        pass
    