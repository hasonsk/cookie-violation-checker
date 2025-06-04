from typing import List, Optional
from datetime import datetime

from schemas.cookie_schema import ActualCookie, ComplianceIssue, ComplianceAnalysisResult
from services.violation_detect_service.violation_analyzer import ViolationAnalyzer
from utils.cookie_utils import extract_main_domain

class ViolationDetectorService:
    """Service chính xử lý compliance analysis"""

    def __init__(self):
        self.analyzer = ViolationAnalyzer()

    async def analyze_website_compliance(self, website_url: str, cookies: List[ActualCookie],
                                 policy_json: Optional[str] = None) -> ComplianceAnalysisResult:
        """Phân tích compliance cho website"""
        main_domain = extract_main_domain(website_url)

        result = self.analyzer.analyze_compliance(policy_json, cookies, main_domain)

        return ComplianceAnalysisResult(
            website_url=website_url,
            analysis_date=datetime.now(),
            total_issues=result.get("total_issues", 0),
            compliance_score=result.get("compliance_score", 0.0),
            issues=[ComplianceIssue(**issue) for issue in result.get("issues", [])],
            statistics=result.get("statistics", {}),
            summary=result.get("summary", {}),
            policy_cookies_count=result.get("policy_cookies_count", 0),
            actual_cookies_count=result.get("actual_cookies_count", 0)
        )
