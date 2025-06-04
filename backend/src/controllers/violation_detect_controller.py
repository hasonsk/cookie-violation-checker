from typing import List
from schemas.cookie_schema import ActualCookie, PolicyCookieList, ComplianceAnalysisResult
from services.violation_detect_service.violation_detector import ViolationDetectorService

class ViolationDetectorController:

    def __init__(self):
        self.violation_service = ViolationDetectorService()

    async def detect_violations(self, cookies: List[ActualCookie], policy_cookies: PolicyCookieList, main_domain: str) -> ComplianceAnalysisResult:
        """Xử lý request submit cookies"""
        # Phân tích compliance
        result = self.violation_service.analyze_website_compliance(cookies, policy_cookies)

        # Log kết quả
        self.violation_service.log_analysis_summary(result, len(cookies))

        # Trả về response
        return result
