from datetime import datetime
from typing import Any, Dict

from src.services.comparator_service.interfaces.compliance_result import IComplianceResultBuilder
from src.schemas.violation import ComplianceAnalysisResult, ComplianceIssue


class ComplianceResultBuilder(IComplianceResultBuilder):
    """Chuyên build kết quả compliance - FUNCTIONAL COHESION"""

    def build_success_result(
        self,
        website_url: str,
        analysis_data: Dict[str, Any]
    ) -> ComplianceAnalysisResult:
        """Chỉ làm 1 việc: build kết quả thành công"""
        return ComplianceAnalysisResult(
            website_url=website_url,
            analysis_date=datetime.now(),
            total_issues=analysis_data.get("total_issues", 0),
            compliance_score=analysis_data.get("compliance_score", 0.0),
            issues=[ComplianceIssue(**issue) for issue in analysis_data.get("issues", [])],
            statistics=analysis_data.get("statistics", {}),
            summary=analysis_data.get("summary", {}),
            policy_cookies_count=analysis_data.get("policy_cookies_count", 0),
            actual_cookies_count=analysis_data.get("actual_cookies_count", 0),
            details=analysis_data.get("details", {})
        )

    def build_error_result(
        self,
        website_url: str,
        error_message: str
    ) -> ComplianceAnalysisResult:
        """Chỉ làm 1 việc: build kết quả lỗi"""
        return ComplianceAnalysisResult(
            website_url=website_url,
            analysis_date=datetime.now(),
            total_issues=0,
            compliance_score=0,
            issues=[],
            statistics={"error": error_message},
            summary={"error_message": "An internal error occurred during analysis."},
            policy_cookies_count=0,
            actual_cookies_count=0,
            details={"error": error_message}
        )
