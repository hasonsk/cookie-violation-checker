from typing import List
from schemas.cookie_schema import Cookie, PolicyCookies, CookieSubmissionResponse
from services.violation_detect_service.violation_detector import ViolationDetectorService

class ViolationDetectorController:

    def __init__(self):
        self.violation_service = ViolationDetectorService()

    async def detect_violations(self, cookies: List[Cookie], policy_cookies: PolicyCookies, main_domain: str) -> CookieSubmissionResponse:
        """Xử lý request submit cookies"""
        # Phân tích compliance
        result = self.violation_service.analyze_cookie_compliance(cookies, policy_cookies)

        # Log kết quả
        self.violation_service.log_analysis_summary(result, len(cookies))

        # Trả về response
        return CookieSubmissionResponse(
            status="received",
            count=len(cookies),
            violation=result
        )
