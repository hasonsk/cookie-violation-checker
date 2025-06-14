from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from src.schemas.cookie import PolicyCookie, ActualCookie

class IComplianceAnalyzer(ABC):
    """Interface cho việc phân tích compliance"""

    @abstractmethod
    def analyze(
        self,
        policy_cookies: List[PolicyCookie],
        actual_cookies: List[ActualCookie],
        domain: str
    ) -> Dict[str, Any]:
        """Phân tích compliance giữa policy và actual cookies"""
        pass
