import json
import logging
from typing import Optional
from dataclasses import asdict

from schemas.cookie_schema import CookieFeature, CookieFeatures
from services.cookies_extract_service.gemini_service import GeminiService
from utils.text_processing import prepare_content, extract_domain, extract_json_from_response
from utils.cookie_classifier import CookieClassifier

logger = logging.getLogger(__name__)

class CookieExtractorService:
    """
    Service for analyzing cookie policies and extracting structured features
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        self.gemini_service = GeminiService(api_key, model)
        self.classifier = CookieClassifier()

    async def extract_cookie_features(self, policy_content: str, table_content: Optional[str] = None) -> CookieFeatures:
        """
        Extract cookie features from policy content using Gemini AI
        """
        try:
            # Prepare content for analysis
            content = prepare_content(policy_content, table_content)

            # Generate content using Gemini
            response = await self.gemini_service.generate_content(content)

            # Parse and validate response
            parsed_features = self._parse_gemini_response(response)

            # Classify cookie types
            for cookie in parsed_features.cookies:
                cookie.feature_type = self.classifier.classify_cookie_type(asdict(cookie))

            logger.info(f"Extracted {len(parsed_features.cookies)} cookie features")
            return parsed_features

        except Exception as e:
            logger.error(f"Error extracting cookie features: {str(e)}")
            return CookieFeatures(is_specific=0, cookies=[])

    async def infer_default_features(self, website_url: str) -> CookieFeatures:
        """
        Infer default cookie features when no policy is available
        """
        try:
            domain = extract_domain(website_url)
            default_cookies = self.classifier.get_common_cookies(domain)

            logger.info(f"Inferred {len(default_cookies)} default cookie features for {domain}")

            return CookieFeatures(
                is_specific=0,
                cookies=default_cookies
            )

        except Exception as e:
            logger.error(f"Error inferring default features: {str(e)}")
            return CookieFeatures(is_specific=0, cookies=[])

    def _parse_gemini_response(self, response: str) -> CookieFeatures:
        """Parse and validate Gemini response"""
        try:
            # Clean response - extract JSON if wrapped in text
            json_str = extract_json_from_response(response)

            # Parse JSON
            data = json.loads(json_str)

            # Validate structure
            if not isinstance(data, dict) or 'is_specific' not in data or 'cookies' not in data:
                raise ValueError("Invalid response structure")

            # Convert to CookieFeatures
            cookies = []
            for cookie_data in data.get('cookies', []):
                cookie = CookieFeature(
                    cookie_name=cookie_data.get('cookie_name'),
                    declared_purpose=cookie_data.get('declared_purpose'),
                    declared_retention=cookie_data.get('declared_retention'),
                    declared_third_parties=cookie_data.get('declared_third_parties', []),
                    declared_description=cookie_data.get('declared_description')
                )
                cookies.append(cookie)

            return CookieFeatures(
                is_specific=int(data.get('is_specific', 0)),
                cookies=cookies
            )

        except Exception as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
            return CookieFeatures(is_specific=0, cookies=[])
