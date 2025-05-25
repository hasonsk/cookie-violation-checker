import json
from typing import Optional
from services.policy_extract_service.policy_extract_service import PolicyExtractService
from schemas.policy_schema import PolicyContent
from utils.cache_utils import CacheManager

class PolicyExtractController:
    """Controller for handling policy extraction requests"""

    async def extract_policy(
        self,
        website_url: str,
        policy_url: Optional[str] = None,
        translate_to_english: bool = True,
        force_refresh: bool = False
    ) -> PolicyContent:
        """
        Extract policy content and return formatted response

        Args:
            website_url: The main website URL
            policy_url: Optional specific policy URL
            translate_to_english: Whether to translate content to English
            force_refresh: Whether to bypass cache

        Returns:
            Formatted policy content dictionary
        """
        async with PolicyExtractService() as extractor:
            result = await extractor.extract_policy_content(
                website_url=website_url,
                policy_url=policy_url,
                translate_to_english=translate_to_english,
                force_refresh=force_refresh
            )

            # Convert to required output format
            return result
