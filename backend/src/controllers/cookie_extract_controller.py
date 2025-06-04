from loguru import logger
from typing import Optional

from services.cookies_extract_service.cookies_extractor import CookieExtractorService
from schemas.cookie_schema import PolicyCookieList

class CookieExtractController:
    def __init__(self, extractor_service: CookieExtractorService):
        self.extractor_service = extractor_service

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
            return features
        except Exception as e:
            logger.error(f"Error in analyze_cookie_policy: {str(e)}")
            return PolicyCookieList(is_specific=0, cookies=[])
