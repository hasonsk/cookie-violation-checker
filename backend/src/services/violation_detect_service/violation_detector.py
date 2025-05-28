import json
import re
from typing import Dict, List, Optional, Any
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

        # Sử dụng policy mặc định nếu không có
        if not policy_json:
            policy_json = self._get_default_policy()

        # Thực hiện phân tích
        result = self.analyzer.analyze_compliance(policy_json, cookies, main_domain)

        # Chuyển đổi sang format để lưu database
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

    def _get_default_policy(self) -> str:
        """Trả về policy mặc định"""
        return json.dumps({
            "cookies": [
                {
                    "cookie_name": "_ga",
                    "declared_purpose": "Analytical",
                    "declared_retention": "13 months",
                    "declared_third_parties": ["Google Analytics"],
                    "declared_description": "Google Analytics tracking cookie."
                },
                {
                    "cookie_name": "session_id",
                    "declared_purpose": "Strictly Necessary",
                    "declared_retention": "Session",
                    "declared_third_parties": ["First Party"],
                    "declared_description": "Session management cookie."
                }
            ]
        })
