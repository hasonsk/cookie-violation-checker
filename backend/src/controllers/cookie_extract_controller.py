import logging
from typing import Optional
from dataclasses import asdict

from services.cookies_extract_service.cookies_extractor import CookieExtractorService
from schemas.cookie_schema import CookieFeatures

logger = logging.getLogger(__name__)

class CookieExtractController:
    """Controller for cookie policy analysis operations"""

    def __init__(self):
        self.extractor_service = CookieExtractorService()

    async def analyze_cookie_policy(self, policy_content: str, table_content: Optional[str] = None) -> dict:
        """
        Analyze cookie policy and return structured features

        Args:
            policy_content: The translated cookie policy text
            table_content: Optional table content with cookie details

        Returns:
            Dictionary containing cookie features
        """
        try:
            features = await self.extractor_service.extract_cookie_features(
                policy_content, table_content
            )
            return asdict(features)
        except Exception as e:
            logger.error(f"Error in analyze_cookie_policy: {str(e)}")
            return asdict(CookieFeatures(is_specific=0, cookies=[]))

    async def get_default_features(self, website_url: str) -> dict:
        """
        Get default cookie features for a website

        Args:
            website_url: URL of the website to analyze

        Returns:
            Dictionary containing inferred cookie features
        """
        try:
            features = await self.extractor_service.infer_default_features(website_url)
            return asdict(features)
        except Exception as e:
            logger.error(f"Error in get_default_features: {str(e)}")
            return asdict(CookieFeatures(is_specific=0, cookies=[]))
