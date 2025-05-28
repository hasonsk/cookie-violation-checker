import logging
from typing import Dict, List
from schemas.cookie_schema import PolicyCookie, CookieType

logger = logging.getLogger(__name__)

class CookieClassifier:
    """Utility class for cookie classification and inference"""

    @staticmethod
    def classify_cookie_type(cookie_feature: dict) -> str:
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

    @staticmethod
    def get_common_cookies(domain: str) -> List[PolicyCookie]:
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
