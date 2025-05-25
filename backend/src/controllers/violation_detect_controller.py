from typing import List
from schemas.cookie_schema import Cookie, CookieSubmissionResponse
from services.violation_detect_service.violation_detector import ViolationDetectorService

class ViolationDetectorController:
    """Controller xử lý các request liên quan đến cookies"""

    def __init__(self):
        self.cookie_service = ViolationDetectorService()

    async def submit_cookies(self, cookies: List[Cookie]) -> CookieSubmissionResponse:
        """Xử lý request submit cookies"""
        print(f"\n🍪 Received cookies: {len(cookies)}")

        # Lấy policy mặc định
        policy_json = self.cookie_service.get_default_policy_json()

        # Phân tích compliance
        result = self.cookie_service.analyze_cookie_compliance(cookies, policy_json)

        # Log kết quả
        self.cookie_service.log_analysis_summary(result, len(cookies))

        # Trả về response
        return CookieSubmissionResponse(
            status="received",
            count=len(cookies),
            violation=result
        )
