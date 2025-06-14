from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Abstract base class cho các LLM providers"""

    @abstractmethod
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using the LLM"""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the LLM provider"""
        pass
