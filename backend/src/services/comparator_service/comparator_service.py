from typing import List, Optional, Dict
from datetime import datetime
from loguru import logger

from src.utils.cookie_utils import extract_main_domain
from src.utils.violation_analyzer_utils import ViolationAnalyzer
from src.models.cookie import PolicyCookie, ActualCookie
from src.schemas.violation import ComplianceIssue, ComplianceAnalysisResult
from src.repositories.violation_repository import ViolationRepository

class ComparatorService:
    def __init__(self, violation_repository: ViolationRepository):
        self.analyzer = ViolationAnalyzer()
        self.violation_repository = violation_repository

    async def analyze_website_compliance(
        self,
        website_url: str,
        cookies: List[Dict],  # Nhận danh sách cookie thô (list of dicts) từ request
        policy_json: Optional[Dict] = None  # Nhận chính sách đã được phân tích (dict) từ request
    ) -> ComplianceAnalysisResult:
        main_domain = extract_main_domain(website_url)

        # Xử lý trường hợp không tìm thấy chính sách cookie
        if policy_json is None:
            logger.warning(f"No policy JSON provided for {website_url}. Analyzing with empty policy.")
            policy_json = {"is_specific": 0, "cookies": []}

        logger.info(f"Starting compliance analysis for {website_url} with {len(cookies)} actual cookies.")

        policy_cookies_parsed = [PolicyCookie(**c) for c in policy_json.get("cookies", [])]

        actual_cookies_parsed = []
        for cookie_data in cookies:
            # Handle 'Session' or invalid expirationDate
            if 'expirationDate' in cookie_data and cookie_data['expirationDate'] == 'Session':
                cookie_data['expirationDate'] = None
            elif 'expirationDate' in cookie_data and not isinstance(cookie_data['expirationDate'], (datetime, type(None))):
                # Attempt to parse if it's a string, otherwise set to None
                try:
                    cookie_data['expirationDate'] = datetime.fromisoformat(cookie_data['expirationDate'].replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    cookie_data['expirationDate'] = None
            actual_cookies_parsed.append(ActualCookie(**cookie_data))

        # Gọi phương thức phân tích của "Rule Engine"
        result = self.analyzer.analyze_compliance(
            policy_cookies=policy_cookies_parsed,
            actual_cookies=actual_cookies_parsed,
            main_domain=main_domain
        )
        logger.debug(f"Type of result from analyzer: {type(result)}")

        # Xử lý các lỗi có thể xảy ra trong quá trình phân tích
        if "error" in result and result["error"]:
            logger.error(f"Analysis for {website_url} failed: {result['error']}")
            # Trả về một kết quả lỗi có cấu trúc
            return ComplianceAnalysisResult(
                website_url=website_url,
                analysis_date=datetime.now(),
                total_issues=0,
                compliance_score=0,
                issues=[],
                statistics={"error": result['error']},
                summary={"error_message": "An internal error occurred during analysis."},
                policy_cookies_count=result.get("policy_cookies_count", 0),
                actual_cookies_count=result.get("actual_cookies_count", 0),
                details={} # Add details field for error case
            )

        logger.info(f"Analysis for {website_url} completed with {result.get('total_issues')} issues.")

        compliance_result = ComplianceAnalysisResult(
            website_url=website_url,
            analysis_date=datetime.now(),
            total_issues=result.get("total_issues", 0),
            compliance_score=result.get("compliance_score", 0.0),
            issues=[ComplianceIssue(**issue) for issue in result.get("issues", [])],
            statistics=result.get("statistics", {}),
            summary=result.get("summary", {}),
            policy_cookies_count=result.get("policy_cookies_count", 0),
            actual_cookies_count=result.get("actual_cookies_count", 0),
            details=result.get("details", {})
        )

        # Lưu kết quả phân tích vào cơ sở dữ liệu
        try:
            result = ComplianceAnalysisResult(
                website_url=compliance_result.website_url,
                analysis_date=compliance_result.analysis_date,
                total_issues=compliance_result.total_issues,
                compliance_score=compliance_result.compliance_score,
                issues=[issue.model_dump() for issue in compliance_result.issues], # Convert Pydantic models to dicts for MongoDB
                statistics=compliance_result.statistics,
                summary=compliance_result.summary,
                policy_cookies_count=compliance_result.policy_cookies_count,
                actual_cookies_count=compliance_result.actual_cookies_count,
                details=compliance_result.details
            )
            await self.violation_repository.create_violation(result.model_dump())
            logger.info(f"Compliance analysis result for {website_url} saved to database.")
            return result
        except Exception as e:
            logger.error(f"Failed to save compliance analysis result for {website_url}: {str(e)}")
            return ComplianceAnalysisResult(
                website_url=website_url,
                analysis_date=datetime.now(),
                total_issues=compliance_result.total_issues,
                compliance_score=compliance_result.compliance_score,
                issues=compliance_result.issues,
                statistics=compliance_result.statistics,
                summary=compliance_result.summary,
                policy_cookies_count=compliance_result.policy_cookies_count,
                actual_cookies_count=compliance_result.actual_cookies_count,
                details={"error": str(e)}
            )
