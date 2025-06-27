import logging
import aiohttp
from typing import Dict, Any, Optional

from src.services.cookie_extractor_service.interfaces.llm_provider import ILLMProvider

logger = logging.getLogger(__name__)


class LlamaLLMProvider(ILLMProvider):
    def __init__(
        self,
        api_endpoint: str,
        # model: str,
        api_key: Optional[str] = None,
        **kwargs
    ):
        self.api_endpoint = api_endpoint
        # self.model = model
        self.api_key = api_key
        self.config = kwargs

        self._validate_configuration()

    def _validate_configuration(self) -> None:
        """Validate the provider configuration"""
        if not self.api_endpoint:
            raise ValueError("API endpoint is required for Llama provider")

        # if not self.model:
        #     raise ValueError("Model name is required for Llama provider")


    async def generate_content(self, content: str, **kwargs) -> str:
        """
        Generate content using Llama API

        Args:
            content: Input content
            **kwargs: Override parameters for this request

        Returns:
            Generated content as string
        """
        try:
            headers = {"Content-Type": "application/json"}
            # if self.api_key:
            #     headers["Authorization"] = f"Bearer {self.api_key}"

            # Use provided parameters or fall back to instance defaults
            # Prepare payload
            payload = {
                # "model": self.model,
                "content": content,
            }

            # Make API request
            timeout = kwargs.get('timeout', 300)  # Default timeout set to 30 seconds
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.post(
                    f"{self.api_endpoint}?key={self.api_key}",
                    json=payload,
                    # headers=headers
                ) as response:

                    if response.status != 200:
                        logger.error(f"Llama API returned status {response.status}: {await response.text()}")
                        return '{"is_specific": 0, "cookies": []}'

                    result = await response.json()

                    logger.debug(f"Llama API response received: {result}")

                    final_result = result.get('generated_text', '{"is_specific": 0, "cookies": []}')
                    logger.debug(f"Llama API response received: {final_result} characters")
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
            "api_endpoint": self.api_endpoint,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "api_key_set": bool(self.api_key),
            "additional_config": self.config
        }
