import requests
from loguru import logger
from src.services.policy_crawler_service.interfaces.content_extractor_interface import IContentExtractor

class RequestsContentExtractor(IContentExtractor):
    """Requests-based content extraction"""

    async def extract_content(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error extracting content with Requests: {e}")
            return ""
