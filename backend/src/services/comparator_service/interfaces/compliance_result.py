from abc import ABC, abstractmethod
from typing import Dict, Any

from src.schemas.violation import ComplianceAnalysisResult, ComplianceIssue

class IComplianceResultBuilder(ABC):
    """Interface để build kết quả compliance"""

    @abstractmethod
    def build_success_result(
        self,
        website_url: str,
        analysis_data: Dict[str, Any]
    ) -> ComplianceAnalysisResult:
        """Build kết quả thành công"""
        pass

    @abstractmethod
    def build_error_result(
        self,
        website_url: str,
        error_message: str
    ) -> ComplianceAnalysisResult:
        """Build kết quả lỗi"""
        pass
