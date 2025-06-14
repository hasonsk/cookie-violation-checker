import logging
import aiohttp
from typing import Dict, Any, Optional

from src.services.cookie_extractor_service.interfaces.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


class LlamaLLMProvider(LLMProvider):
    """
    Llama LLM Provider - Functional Cohesion
    Single responsibility: Handle communication with Llama API
    """

    def __init__(
        self,
        api_endpoint: str,
        model: str,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize Llama provider

        Args:
            api_endpoint: API endpoint URL
            model: Model name (e.g., 'llama-3.1-8b')
            api_key: Optional API key for authentication
            temperature: Generation temperature (0.0 to 1.0)
            max_tokens: Maximum output tokens
            timeout: Request timeout in seconds
            **kwargs: Additional configuration parameters
        """
        self.api_endpoint = api_endpoint
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.config = kwargs

        self._validate_configuration()

    def _validate_configuration(self) -> None:
        """Validate the provider configuration"""
        if not self.api_endpoint:
            raise ValueError("API endpoint is required for Llama provider")

        if not self.model:
            raise ValueError("Model name is required for Llama provider")

        if not (0.0 <= self.temperature <= 1.0):
            raise ValueError("Temperature must be between 0.0 and 1.0")

        if self.max_tokens <= 0:
            raise ValueError("Max tokens must be greater than 0")

        if self.timeout <= 0:
            raise ValueError("Timeout must be greater than 0")

    async def generate_content(self, prompt: str, **kwargs) -> str:
        """
        Generate content using Llama API

        Args:
            prompt: Input prompt
            **kwargs: Override parameters for this request

        Returns:
            Generated content as string
        """
        try:
            # Prepare headers
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            # Use provided parameters or fall back to instance defaults
            temperature = kwargs.get('temperature', self.temperature)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            timeout = kwargs.get('timeout', self.timeout)

            # Prepare payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False,
                **{k: v for k, v in kwargs.items() if k not in ['temperature', 'max_tokens', 'timeout']}
            }

            # Make API request
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.post(
                    self.api_endpoint,
                    json=payload,
                    headers=headers
                ) as response:

                    if response.status != 200:
                        logger.error(f"Llama API returned status {response.status}: {await response.text()}")
                        return '{"is_specific": 0, "cookies": []}'

                    result = await response.json()

                    # Extract text from response (format may vary by API)
                    if "choices" in result and result["choices"]:
                        generated_text = result["choices"][0].get("text", "")
                    elif "response" in result:
                        generated_text = result["response"]
                    elif "output" in result:
                        generated_text = result["output"]
                    else:
                        logger.warning(f"Unexpected Llama API response format: {result}")
                        generated_text = ""

                    final_result = generated_text or '{"is_specific": 0, "cookies": []}'
                    logger.debug(f"Llama API response received: {len(final_result)} characters")
                    return final_result

        except aiohttp.ClientError as e:
            logger.error(f"Llama API client error: {str(e)}")
            return '{"is_specific": 0, "cookies": []}'

        except Exception as e:
            logger.error(f"Llama API error: {str(e)}")
            return '{"is_specific": 0, "cookies": []}'

    def get_provider_name(self) -> str:
        """Get provider name"""
        return "Llama"

    def get_model_info(self) -> Dict[str, Any]:
        """Get current model configuration"""
        return {
            "provider": self.get_provider_name(),
            "model": self.model,
            "api_endpoint": self.api_endpoint,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "api_key_set": bool(self.api_key),
            "additional_config": self.config
        }
