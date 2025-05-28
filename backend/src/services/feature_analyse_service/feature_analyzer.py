"""
Feature Analyzer Service - Cookie Policy Analysis with Gemini AI Integration
Extracts structured cookie features from policy documents and handles feature inference
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel
from dataclasses import dataclass, asdict
from enum import Enum
from dotenv import dotenv_values
import re
from urllib.parse import urlparse

# Google Gemini imports
from google import genai
from google.genai import types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CookieType(Enum):
    """Cookie classification types"""
    SPECIFIC = "specific"
    GENERAL = "general"
    UNDEFINED = "undefined"

class CookiePurpose(Enum):
    """Standard cookie purposes"""
    STRICTLY_NECESSARY = "Strictly Necessary"
    FUNCTIONALITY = "Functionality"
    ANALYTICAL = "Analytical"
    TARGETING = "Targeting/Advertising/Marketing"
    PERFORMANCE = "Performance"
    SOCIAL_SHARING = "Social Sharing"
    UNKNOWN = "Unknown"

class PolicyCookie(BaseModel):
    """Individual cookie feature structure"""
    cookie_name: Optional[str]
    declared_purpose: Optional[str]
    declared_retention: Optional[str]
    declared_third_parties: List[str]
    declared_description: Optional[str]
    feature_type: str = CookieType.UNDEFINED.value

class PolicyCookies(BaseModel):
    """Complete cookie features response structure"""
    is_specific: int
    cookies: List[PolicyCookie]

class FeatureAnalyzerService:
    """
    Service for analyzing cookie policies and extracting structured features
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        """
        Initialize the Feature Analyzer Service

        Args:
            api_key: Google AI API key (optional, can be set via environment variable)
        """
        # Load environment variables
        # config = dotenv_values(".env")
        # gemini_api_key = config.get("GEMINI_API_KEY")

        # if gemini_api_key:
        #   gemini_api_key = os.environ["GEMINI_API_KEY"]
        # else:
        #   logger.warning("GEMINI_API_KEY not found in environment or .env file")

        # self.api_key = gemini_api_key
        self.api_key = "AIzaSyBpPwWeKxESlPQQMA6qo8AtcVb-yyA3LSc"
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be provided or set as environment variable")
        self.model = model

        # System prompt for cookie extraction
        self.SYSTEM_PROMPT = """
ROLE: You are a cookie policy analysis expert.
Your task is to read a cookie policy text and extract detailed information about each cookie mentioned in that policy.

RESPONSE Format: Return ONLY a valid JSON object with this exact structure:
{
  "is_specific": 1,
  "cookies": [
    {
      "cookie_name": "cookie_name",
      "declared_purpose": "declared_purpose",
      "declared_retention": "declared_retention",
      "declared_third_parties": ["declared_third_parties"],
      "declared_description": "declared_description"
    }
  ]
}

If no specific cookies are described, return:
{
  "is_specific": 0,
  "cookies": []
}

Specific Requirements:
1. Read and Analyze the Text: Carefully read the entire content to understand cookie types, purposes, storage duration, and ownership.

2. Extract Information for Each Cookie:
   - "cookie_name": Technical or descriptive name exactly as mentioned
   - "declared_purpose": Choose from: "Strictly Necessary", "Functionality", "Analytical", "Targeting/Advertising/Marketing", "Performance", "Social Sharing", or null
   - "declared_retention": Duration (e.g., "6 months", "24 hours", "Session", "Persistent", "Until deleted")
   - "declared_third_parties": Array of third parties, use ["First Party"] for first-party cookies
   - "declared_description": Direct content from text without fabrication

3. Set is_specific to 1 if specific cookies are found, 0 if only general descriptions exist.

IMPORTANT: Return ONLY valid JSON, no additional text or explanations.
"""

    async def extract_cookie_features(self, policy_content: str, table_content: Optional[str] = None) -> PolicyCookies:
        """
        Extract cookie features from policy content using Gemini AI

        Args:
            policy_content: The translated cookie policy text
            table_content: Optional table content with cookie details

        Returns:
            PolicyCookies object with extracted information
        """
        try:
            # Prepare content for analysis
            content = self._prepare_content(policy_content, table_content)

            # Generate content using Gemini
            response = await self._generate_with_gemini(content)

            # Parse and validate response
            parsed_features = self._parse_gemini_response(response)

            # Classify cookie types
            for cookie in parsed_features.cookies:
                cookie.feature_type = self.classify_cookie_type(asdict(cookie))

            logger.info(f"Extracted {len(parsed_features.cookies)} cookie features")
            return parsed_features

        except Exception as e:
            logger.error(f"Error extracting cookie features: {str(e)}")
            # Return default structure on error
            return PolicyCookies(is_specific=0, cookies=[])

    async def infer_default_features(self, website_url: str) -> PolicyCookies:
        """
        Infer default cookie features when no policy is available

        Args:
            website_url: URL of the website to analyze

        Returns:
            PolicyCookies with inferred common cookies
        """
        try:
            domain = self._extract_domain(website_url)

            # Common cookies based on website type and domain
            default_cookies = self._get_common_cookies(domain)

            # Add domain-specific inferred cookies
            # inferred_cookies = self._infer_domain_specific_cookies(domain)
            # default_cookies.extend(inferred_cookies)

            logger.info(f"Inferred {len(default_cookies)} default cookie features for {domain}")

            return PolicyCookies(
                is_specific=0,
                cookies=default_cookies
            )

        except Exception as e:
            logger.error(f"Error inferring default features: {str(e)}")
            return PolicyCookies(is_specific=0, cookies=[])

    def classify_cookie_type(self, cookie_feature: dict) -> str:
        """
        Classify cookie type based on feature characteristics

        Args:
            cookie_feature: Dictionary containing cookie feature data

        Returns:
            CookieType classification as string
        """
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
        """Prepare content for Gemini analysis"""
        content_parts = []

        if policy_content and policy_content.strip():
            content_parts.append(f"Cookie policy: {policy_content}")

        if table_content and table_content.strip():
            content_parts.append(f"Table: {table_content}")

        if not content_parts:
            content_parts.append("No specific cookie policy content provided.")

        return "\n\n".join(content_parts)

    async def _generate_with_gemini(self, content: str) -> str:
        """Generate response using Gemini API"""
        try:
            # Create the model client
            client = genai.Client(api_key=self.api_key)

            # Prepare the prompt
            prompt = f"{self.SYSTEM_PROMPT}\n\nContent to analyze:\n{content}"

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
                    temperature=0.1,
                    max_output_tokens=2048,
                )
            )

            return response.text if response.text else "{\"is_specific\": 0, \"cookies\": []}"

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return "{\"is_specific\": 0, \"cookies\": []}"

    def _parse_gemini_response(self, response: str) -> PolicyCookies:
        """Parse and validate Gemini response"""
        try:
            # Clean response - extract JSON if wrapped in text
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
                feature_type=CookieType.GENERAL.value
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
                    feature_type=CookieType.SPECIFIC.value
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
                    declared_description="Shopping cart functionality",
                    feature_type=CookieType.SPECIFIC.value
                ),
                PolicyCookie(
                    cookie_name=None,
                    declared_purpose="Targeting/Advertising/Marketing",
                    declared_retention="30 days",
                    declared_third_parties=["Facebook", "Google Ads"],
                    declared_description="Marketing and advertising cookies",
                    feature_type=CookieType.GENERAL.value
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
                    feature_type=CookieType.GENERAL.value
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
