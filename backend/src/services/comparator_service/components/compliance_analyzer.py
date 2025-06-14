from typing import Any, Dict, List

from src.schemas.cookie import PolicyCookie, ActualCookie
from src.services.comparator_service.interfaces.compliance_analyzer import IComplianceAnalyzer
from src.services.comparator_service.components.compliance_comparator import ComplianceComparator


class ComplianceAnalyzer(IComplianceAnalyzer):
    """Chuyên phân tích compliance - FUNCTIONAL COHESION"""

    def __init__(self, compliance_analyzer=ComplianceComparator):
        self.compliance_analyzer = compliance_analyzer

    def analyze(
        self,
        policy_cookies: List[PolicyCookie],
        actual_cookies: List[ActualCookie],
        domain: str
    ) -> Dict[str, Any]:
        return self.compliance_analyzer.analyze_compliance(
            policy_cookies=policy_cookies,
            actual_cookies=actual_cookies,
            main_domain=domain
        )
