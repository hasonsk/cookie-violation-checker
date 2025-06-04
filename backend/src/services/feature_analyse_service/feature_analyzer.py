import os
import json
import asyncio
from loguru import logger
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel
from dataclasses import dataclass, asdict
from enum import Enum
from dotenv import load_dotenv, find_dotenv
import re
from urllib.parse import urlparse

# Google Gemini imports
from google import genai
from google.genai import types

load_dotenv(find_dotenv())

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

class CookieType(Enum):
    """Cookie classification types"""
    SPECIFIC = "specific"
    GENERAL = "general"
    UNDEFINED = "undefined"

class PolicyCookie(BaseModel):
    """Individual cookie feature structure"""
    cookie_name: Optional[str]
    declared_purpose: Optional[str]
    declared_retention: Optional[str]
    declared_third_parties: List[str]
    declared_description: Optional[str]

class PolicyCookies(BaseModel):
    """Complete cookie features response structure"""
    is_specific: int
    cookies: List[PolicyCookie]

class FeatureAnalyzerService:
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be set")
        self.model = model

        # System prompt for cookie extraction
        with open("prompts/system_prompt.txt", "r", encoding="utf-8") as f:
            self.SYSTEM_PROMPT = f.read()

    async def extract_cookie_features(self, policy_content: str, table_content: Optional[str] = None) -> PolicyCookies:
        try:
            # Prepare content for analysis
            content = self._prepare_content(policy_content, table_content)

            # Generate content using Gemini
            response = await self._generate_with_gemini(content)

            # Parse and validate response
            parsed_features = self._parse_gemini_response(response)

            logger.info(f"Extracted {len(parsed_features.cookies)} cookie features")
            return parsed_features

        except Exception as e:
            logger.error(f"Error extracting cookie features: {str(e)}")
            # Return default structure on error
            return PolicyCookies(is_specific=0, cookies=[])

    async def infer_default_features(self, website_url: str) -> PolicyCookies:
        try:
            domain = self._extract_domain(website_url)

            default_cookies = self._get_common_cookies(domain)

            logger.info(f"Inferred {len(default_cookies)} default cookie features for {domain}")

            return PolicyCookies(
                is_specific=0,
                cookies=default_cookies
            )

        except Exception as e:
            logger.error(f"Error inferring default features: {str(e)}")
            return PolicyCookies(is_specific=0, cookies=[])

    def classify_cookie_type(self, cookie_feature: dict) -> str:
        try:
            # Check if cookie has specific name and detailed information
            has_name = cookie_feature.get('cookie_name') is not None
            has_description = cookie_feature.get('declared_description') is not None
            has_purpose = cookie_feature.get('declared_purpose') is not None
            has_retention = cookie_feature.get('declared_retention') is not None

            # Specific: Has name and at least 2 other attributes
            if has_name and sum([has_description, has_purpose, has_retention]) >= 2:
                return CookieType.SPECIFIC.value

            # General: Has purpose but lacks specific details
            elif has_purpose and not has_name:
                return CookieType.GENERAL.value

            # Undefined: Insufficient information
            else:
                return CookieType.UNDEFINED.value

        except Exception as e:
            logger.error(f"Error classifying cookie type: {str(e)}")
            return CookieType.UNDEFINED.value

    def _prepare_content(self, policy_content: str, table_content: Optional[str] = None) -> str:
        content_parts = []

        if policy_content and policy_content.strip():
            content_parts.append(f"Cookie policy: {policy_content}")

        if table_content and table_content.strip():
            content_parts.append(f"Table: {table_content}")

        if not content_parts:
            content_parts.append("No specific cookie policy content provided.")

        return "\n\n".join(content_parts)

    def extract_json_content(self, response_text: str) -> str:
        if not response_text:
            return '{"is_specific": 0, "cookies": []}'

        cleaned_text = response_text.strip()

        json_pattern = r'```(?:json)?\s*(.*?)\s*```'
        match = re.search(json_pattern, cleaned_text, re.DOTALL)

        if match:
            json_content = match.group(1).strip()
        else:
            json_content = cleaned_text

        return json_content


    async def _generate_with_gemini(self, content: str) -> str:
        try:
            # Create the model client
            client = genai.Client(api_key=self.api_key)

            # Prepare the prompt
            prompt = f"{self.SYSTEM_PROMPT}\n\nContent to analyze:\n{content}"

            response = client.models.generate_content(
                model=self.model,
                contents=[
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)]
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=2048,
                )
            )

            return self.extract_json_content(response.text)

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return "{\"is_specific\": 0, \"cookies\": []}"

    def _parse_gemini_response(self, response: str) -> PolicyCookies:
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
            else:
                json_str = response

            # Parse JSON
            data = json.loads(json_str)

            # Validate structure
            if not isinstance(data, dict) or 'is_specific' not in data or 'cookies' not in data:
                raise ValueError("Invalid response structure")

            # Convert to PolicyCookies
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

            return PolicyCookies(
                is_specific=int(data.get('is_specific', 0)),
                cookies=cookies
            )

        except Exception as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
            return PolicyCookies(is_specific=0, cookies=[])

    def _extract_domain(self, website_url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(website_url)
            return parsed.netloc or parsed.path
        except:
            return website_url

    def _get_common_cookies(self, domain: str) -> List[PolicyCookie]:
        """Get common cookies based on domain patterns"""
        common_cookies = [
            PolicyCookie(
                cookie_name=None,
                declared_purpose="Strictly Necessary",
                declared_retention="Session",
                declared_third_parties=["First Party"],
                declared_description="Essential cookies for basic website functionality",
            )
        ]

        # Add analytics cookies for most domains
        if not any(pattern in domain.lower() for pattern in ['gov', 'edu', 'internal']):
            common_cookies.append(
                PolicyCookie(
                    cookie_name="_ga",
                    declared_purpose="Analytical",
                    declared_retention="13 months",
                    declared_third_parties=["Google Analytics"],
                    declared_description="Google Analytics tracking cookie",
                )
            )

        return common_cookies

    def _infer_domain_specific_cookies(self, domain: str) -> List[PolicyCookie]:
        """Infer cookies based on domain characteristics"""
        inferred_cookies = []

        # E-commerce sites
        if any(keyword in domain.lower() for keyword in ['shop', 'store', 'cart', 'buy', 'commerce']):
            inferred_cookies.extend([
                PolicyCookie(
                    cookie_name="cart_session",
                    declared_purpose="Strictly Necessary",
                    declared_retention="Session",
                    declared_third_parties=["First Party"],
                    declared_description="Shopping cart functionality"
                ),
                PolicyCookie(
                    cookie_name=None,
                    declared_purpose="Targeting/Advertising/Marketing",
                    declared_retention="30 days",
                    declared_third_parties=["Facebook", "Google Ads"],
                    declared_description="Marketing and advertising cookies"
                )
            ])

        # Social media or content sites
        if any(keyword in domain.lower() for keyword in ['social', 'blog', 'news', 'media']):
            inferred_cookies.append(
                PolicyCookie(
                    cookie_name=None,
                    declared_purpose="Social Sharing",
                    declared_retention="Persistent",
                    declared_third_parties=["Facebook", "Twitter", "LinkedIn"],
                    declared_description="Social media integration cookies",
                                    )
            )

        return inferred_cookies

# Example usage and testing
async def main():
    """Example usage of the Feature Analyzer Service"""

    # Initialize service
    analyzer = FeatureAnalyzerService()

    # Example 1: Extract from policy content
    policy_content = """
    Our website uses the following cookies:

    _ga: This Google Analytics cookie tracks user sessions and behavior.
    It expires after 13 months and is provided by Google Analytics.

    session_id: Essential cookie for maintaining user login sessions.
    This cookie expires when the browser is closed.

    marketing_pref: Used for targeted advertising and marketing campaigns.
    Expires after 30 days and may be shared with Facebook and Google Ads.
    """

    table_content = """
    Cookie Name | Purpose | Retention | Third Party
    _ga | Analytics | 13 months | Google Analytics
    session_id | Necessary | Session | First Party
    marketing_pref | Marketing | 30 days | Facebook, Google Ads
    """

    print("=== Extracting from Policy Content ===")
    features = await analyzer.extract_cookie_features(policy_content, table_content)
    print(json.dumps(asdict(features), indent=2, default=str))

    # Example 2: Infer default features
    # print("\n=== Inferring Default Features ===")
    # default_features = await analyzer.infer_default_features("https://example-shop.com")
    # print(json.dumps(asdict(default_features), indent=2, default=str))

    # Example 3: Cookie classification
    print("\n=== Cookie Classification Examples ===")
    test_cookies = [
        {
            "cookie_name": "_ga",
            "declared_purpose": "Analytical",
            "declared_retention": "13 months",
            "declared_description": "Google Analytics tracking"
        },
        {
            "cookie_name": "CookieConsent",
            "declared_purpose": "Strictly Necessary",
            "declared_retention": None,
            "declared_description": None
        },
        {
            "cookie_name": "None",
            "declared_purpose": None,
            "declared_retention": None,
            "declared_description": None
        }
    ]

    for i, cookie in enumerate(test_cookies):
        classification = analyzer.classify_cookie_type(cookie)
        print(f"Cookie {i+1}: {classification}")

if __name__ == "__main__":
    # Run example
    asyncio.run(main())
