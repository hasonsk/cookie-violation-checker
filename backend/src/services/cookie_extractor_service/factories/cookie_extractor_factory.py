from enum import Enum
from typing import Dict, Any

from src.services.cookie_extractor_service.interfaces.llm_provider import ILLMProvider
from src.services.cookie_extractor_service.providers.gemini_provider import GeminiLLMProvider
from src.services.cookie_extractor_service.providers.llama_provider import LlamaLLMProvider


class LLMProviderType(Enum):
    """Enumeration of supported LLM provider types"""
    GEMINI = "gemini"
    LLAMA = "llama"

class CookieExtractorFactory:
    """
    LLM Provider Factory - Functional Cohesion
    Single responsibility: Create LLM provider instances
    """

    @staticmethod
    def create_provider(provider_type: LLMProviderType, **config) -> ILLMProvider:
        """
        Create LLM provider based on type and configuration

        Args:
            provider_type: Type of LLM provider to create
            **config: Configuration parameters for the provider

        Returns:
            Configured LLM provider instance

        Raises:
            ValueError: If provider type is not supported
            TypeError: If required configuration is missing
        """
        if provider_type == LLMProviderType.GEMINI:
            return CookieExtractorFactory._create_gemini_provider(**config)

        elif provider_type == LLMProviderType.LLAMA:
            return CookieExtractorFactory._create_llama_provider(**config)
        else:
            raise ValueError(f"Unsupported LLM provider type: {provider_type}")

    @staticmethod
    def _create_gemini_provider(**config) -> GeminiLLMProvider:
        """Create Gemini provider with validation"""
        required_fields = ["api_key", "model"]
        CookieExtractorFactory._validate_required_config(required_fields, config, "Gemini")

        return GeminiLLMProvider(
            api_key=config["api_key"],
            model=config["model"],
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 1000),
            **{k: v for k, v in config.items() if k not in ["api_key", "model", "temperature", "max_tokens"]}
        )

    @staticmethod
    def _create_llama_provider(**config) -> LlamaLLMProvider:
        """Create Llama provider with validation"""
        required_fields = ["api_endpoint", "model"]
        CookieExtractorFactory._validate_required_config(required_fields, config, "Llama")

        return LlamaLLMProvider(
            api_endpoint=config["api_endpoint"],
            model=config["model"],
            api_key=config.get("api_key"),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 1000),
            timeout=config.get("timeout", 30),
            **{k: v for k, v in config.items()
               if k not in ["api_endpoint", "model", "api_key", "temperature", "max_tokens", "timeout"]}
        )
    @staticmethod
    def _validate_required_config(required_fields: list, config: Dict[str, Any], provider_name: str) -> None:
        """Validate that required configuration fields are present"""
        missing_fields = [field for field in required_fields if field not in config or not config[field]]

        if missing_fields:
            raise TypeError(
                f"Missing required configuration for {provider_name} provider: {', '.join(missing_fields)}"
            )

    @classmethod
    def get_supported_providers(cls) -> list:
        """Get list of supported provider types"""
        return [provider.value for provider in LLMProviderType]

    @classmethod
    def get_provider_requirements(cls, provider_type: LLMProviderType) -> Dict[str, Any]:
        """
        Get configuration requirements for a specific provider type

        Args:
            provider_type: Provider type to get requirements for

        Returns:
            Dictionary with required and optional configuration fields
        """
        requirements = {
            LLMProviderType.GEMINI: {
                "required": ["api_key", "model"],
                "optional": ["temperature", "max_tokens"],
                "defaults": {"temperature": 0.7, "max_tokens": 1000}
            },
            LLMProviderType.LLAMA: {
                "required": ["api_endpoint", "model"],
                "optional": ["api_key", "temperature", "max_tokens", "timeout"],
                "defaults": {"temperature": 0.7, "max_tokens": 1000, "timeout": 30}
            },
        }

        return requirements.get(provider_type, {"required": [], "optional": [], "defaults": {}})
