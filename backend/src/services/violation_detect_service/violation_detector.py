"""
Module này chứa ViolationDetectorService, đóng vai trò là điểm vào (entry point)
để điều phối quá trình phân tích tuân thủ cookie.
"""
from typing import List, Optional, Dict
from datetime import datetime
from loguru import logger

# Import các schema cần thiết để định dạng dữ liệu
from schemas.cookie_schema import (
    ComplianceIssue,
    ComplianceAnalysisResult,
    PolicyCookie, # Add this import
    ActualCookie,
    PolicyCookieList # Add this import
)

# Import các tiện ích
from utils.cookie_utils import extract_main_domain

# Import "Rule Engine" đã được tối ưu hóa
from .violation_analyzer import ViolationAnalyzer


class ViolationDetectorService:
    """
    Service chính điều phối việc phát hiện vi phạm.
    Nó nhận dữ liệu thô, gọi ViolationAnalyzer để xử lý,
    và định dạng kết quả cuối cùng.
    """

    def __init__(self):
        """
        Khởi tạo service với một instance của ViolationAnalyzer.
        Analyzer sẽ tự động nạp tất cả các quy tắc từ `violation_rules.py`.
        """
        self.analyzer = ViolationAnalyzer()

    async def analyze_website_compliance(
        self,
        website_url: str,
        cookies: List[Dict],  # Nhận danh sách cookie thô (list of dicts) từ request
        policy_json: Optional[PolicyCookieList] = None  # Nhận chính sách đã được phân tích (dict) từ request
    ) -> ComplianceAnalysisResult:
        """
        Hàm chính để điều phối toàn bộ quá trình phân tích tuân thủ.

        Args:
            website_url: URL của trang web đang được phân tích.
            cookies: Danh sách các cookie thực tế được thu thập.
            policy_json: Dữ liệu có cấu trúc của chính sách cookie.

        Returns:
            Một đối tượng ComplianceAnalysisResult chứa kết quả phân tích toàn diện.
        """
        main_domain = extract_main_domain(website_url)

        # Xử lý trường hợp không tìm thấy chính sách cookie
        if policy_json is None:
            logger.warning(f"No policy JSON provided for {website_url}. Analyzing with empty policy.")
            policy_json = {"is_specific": 0, "cookies": []}

        logger.info(f"Starting compliance analysis for {website_url} with {len(cookies)} actual cookies.")

        # Convert raw policy_json and actual_cookies to Pydantic models
        # Assuming policy_json["cookies"] is a list of dicts that can be converted to PolicyCookie
        # policy_cookies_parsed = [PolicyCookie(**c) for c in policy_json.get("cookies", [])]
        policy_cookies_parsed = [PolicyCookie(**c.dict()) for c in policy_json["cookies"]]
        actual_cookies_parsed = [ActualCookie(**c) for c in cookies]

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
                actual_cookies_count=result.get("actual_cookies_count", 0)
            )

        logger.info(f"Analysis for {website_url} completed with {result.get('total_issues')} issues.")

        # Xây dựng và trả về đối tượng kết quả cuối cùng theo schema
        return ComplianceAnalysisResult(
            website_url=website_url,
            analysis_date=datetime.now(),
            total_issues=result.get("total_issues", 0),
            compliance_score=result.get("compliance_score", 0.0),
            # Đảm bảo các 'issues' được chuyển đổi thành đối tượng Pydantic
            issues=[ComplianceIssue(**issue) for issue in result.get("issues", [])],
            statistics=result.get("statistics", {}),
            summary=result.get("summary", {}),
            policy_cookies_count=result.get("policy_cookies_count", 0),
            actual_cookies_count=result.get("actual_cookies_count", 0)
        )
