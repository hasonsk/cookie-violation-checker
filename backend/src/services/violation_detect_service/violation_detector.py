from typing import List, Dict, Any
from datetime import datetime
from schemas.cookie_schema import Cookie, ActualCookie
from services.violation_detect_service.violation_analyzer import ViolationAnalyzer

class ViolationDetectorService:
    """Service xử lý logic nghiệp vụ cho cookies"""

    def __init__(self):
        self.analyzer = ViolationAnalyzer()

    def convert_cookies_to_actual(self, cookies: List[Cookie]) -> List[ActualCookie]:
        """Chuyển đổi Cookie schema thành ActualCookie dataclass"""
        actual_cookies = []
        for cookie in cookies:
            actual_cookie = ActualCookie(
                name=cookie.name,
                value=cookie.value or "",
                domain=cookie.domain,
                expires=cookie.expirationDate.replace(tzinfo=None) if cookie.expirationDate else None,
                secure=cookie.secure,
                httpOnly=cookie.httpOnly,
                sameSite=cookie.sameSite,
                thirdParties=[]  # Placeholder for third-party requests
            )
            actual_cookies.append(actual_cookie)
        return actual_cookies

    def analyze_cookie_compliance(self, cookies: List[Cookie], policy_json: str, main_domain: str = "example.com") -> Dict[str, Any]:
        """Phân tích độ tuân thủ của cookies"""
        # Chuyển đổi cookies
        actual_cookies = self.convert_cookies_to_actual(cookies)

        # Phân tích compliance
        result = self.analyzer.analyze_compliance(policy_json, actual_cookies, main_domain)

        return result

    def log_analysis_summary(self, result: Dict[str, Any], cookie_count: int):
        """Log tóm tắt kết quả phân tích"""
        print("=== COOKIE POLICY COMPLIANCE ANALYSIS ===")
        print(f"Total Issues Found: {result['total_issues']}")
        print(f"Compliance Score: {result['compliance_score']}/100")
        print(f"Policy Cookies: {result['policy_cookies_count']}")
        print(f"Actual Cookies: {result['actual_cookies_count']}")

        print("\n=== ISSUES BY SEVERITY ===")
        for severity, count in result['statistics']['by_severity'].items():
            print(f"{severity}: {count}")

    def get_default_policy_json(self) -> str:
        """Trả về policy JSON mặc định"""
        return """{
            "is_specific": 1,
            "cookies": [
                {
                    "cookie_name": "_ga",
                    "declared_purpose": "Analytical",
                    "declared_retention": "13 months",
                    "declared_third_parties": ["Google Analytics"],
                    "declared_description": "This Google Analytics cookie tracks user sessions and behavior."
                },
                {
                    "cookie_name": "session_id",
                    "declared_purpose": "Strictly Necessary",
                    "declared_retention": "Session",
                    "declared_third_parties": ["First Party"],
                    "declared_description": "Essential cookie for maintaining user login sessions."
                },
                {
                    "cookie_name": "check_rule_5",
                    "declared_purpose": "Strictly Necessary",
                    "declared_retention": "short-term",
                    "declared_third_parties": ["First Party"],
                    "declared_description": "Essential cookie for maintaining user login sessions."
                }
            ]
        }"""
