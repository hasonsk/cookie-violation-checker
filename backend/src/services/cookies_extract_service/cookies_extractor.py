import json
from loguru import logger
from typing import Optional

from src.schemas.cookie_schema import PolicyCookie, PolicyCookieList
from src.services.cookies_extract_service.gemini_service import GeminiService
from src.utils.text_processing import prepare_content, extract_domain, extract_json_from_response
from src.configs.cookie_extract_conf import GEMINI_API_KEY, GEMINI_MODEL

class CookieExtractorService:
    """
    Service for analyzing cookie policies and extracting structured features
    """

    def __init__(self, api_key: Optional[str] = GEMINI_API_KEY, model: str = GEMINI_MODEL):
        self.gemini_service = GeminiService(api_key, model)

    async def extract_cookie_features(self, policy_content: str, table_content: Optional[str] = None) -> PolicyCookieList:
        """
        Extract cookie features from policy content using Gemini AI
        """
        try:
            # Prepare content for analysis
            content = prepare_content(policy_content, table_content)

            # Generate content using Gemini
            response = await self.gemini_service.generate_content(content)
            logger.warning(f"Response: {response}")

            # Parse and validate response
            parsed_features = self._parse_gemini_response(response)

            return parsed_features

        except Exception as e:
            logger.error(f"Error extracting cookie features: {str(e)}")
            logger.exception("Traceback:")
            return PolicyCookieList(is_specific=0, cookies=[])

    def _parse_gemini_response(self, response: str) -> PolicyCookieList:
        try:
            # Clean response - extract JSON if wrapped in text
            json_str = extract_json_from_response(response)

            # Parse JSON
            data = json.loads(json_str)


            # Validate structure
            if not isinstance(data, dict) or 'is_specific' not in data or 'cookies' not in data:
                raise ValueError("Invalid response structure")

            # Convert to PolicyCookieList
            cookies = []
            for cookie_data in data.get('cookies', []):
                cookie = PolicyCookie(
                    cookie_name=cookie_data.get('cookie_name'),
                    declared_purpose=cookie_data.get('declared_purpose'),
                    declared_retention=cookie_data.get('declared_retention'),
                    declared_third_parties=cookie_data.get('declared_third_parties', []),
                    declared_description=cookie_data.get('declared_description')
                )
                cookies.append(cookie)

            return PolicyCookieList(
                is_specific=int(data.get('is_specific', 0)),
                cookies=cookies
            )

        except Exception as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
            return PolicyCookieList(is_specific=0, cookies=[])
