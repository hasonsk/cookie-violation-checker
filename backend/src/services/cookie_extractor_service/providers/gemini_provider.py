import logging
from typing import Dict, Any, Optional

from src.services.cookie_extractor_service.interfaces.llm_provider import ILLMProvider

logger = logging.getLogger(__name__)


class GeminiLLMProvider(ILLMProvider):
    """
    Gemini LLM Provider - Functional Cohesion
    Single responsibility: Handle communication with Gemini API
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ):
        """
        Initialize Gemini provider

        Args:
            api_key: Gemini API key
            model: Model name (e.g., 'gemini-pro')
            temperature: Generation temperature (0.0 to 1.0)
            max_tokens: Maximum output tokens
            **kwargs: Additional configuration parameters
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.config = kwargs

        self._validate_configuration()

    def _validate_configuration(self) -> None:
        """Validate the provider configuration"""
        if not self.api_key:
            raise ValueError("API key is required for Gemini provider")

        if not self.model:
            raise ValueError("Model name is required for Gemini provider")

        if not (0.0 <= self.temperature <= 1.0):
            raise ValueError("Temperature must be between 0.0 and 1.0")

        if self.max_tokens <= 0:
            raise ValueError("Max tokens must be greater than 0")

    async def generate_content(self, prompt: str, **kwargs) -> str:
        """
        Generate content using Gemini API

        Args:
            prompt: Input prompt
            **kwargs: Override parameters for this request

        Returns:
            Generated content as string
        """
        try:
            from google import genai
            from google.genai import types

            # Create client
            client = genai.Client(api_key=self.api_key)

            # Use provided parameters or fall back to instance defaults
            temperature = kwargs.get('temperature', self.temperature)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)

            # Generate content
            response = client.models.generate_content(
                model=self.model,
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)]
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )

            result = response.text if response.text else '{"is_specific": 0, "cookies": []}'
            logger.debug(f"Gemini API response received: {len(result)} characters")
            return result

        except ImportError as e:
            logger.error(f"Google Generative AI library not found: {e}")
            raise RuntimeError("Please install google-generativeai package") from e

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            # Return default JSON response on error
            return '{"is_specific": 0, "cookies": []}'

    def get_provider_name(self) -> str:
        """Get provider name"""
        return "Gemini"

    def get_model_info(self) -> Dict[str, Any]:
        """Get current model configuration"""
        return {
            "provider": self.get_provider_name(),
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "api_key_set": bool(self.api_key),
            "additional_config": self.config
        }
