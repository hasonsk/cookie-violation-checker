from abc import ABC, abstractmethod
from typing import List, Dict

from src.models.cookie import PolicyCookie, ActualCookie

class ICookieDataProcessor(ABC):
    """Interface để xử lý dữ liệu cookie thô"""

    @abstractmethod
    def process_policy_cookies(self, policy_json: Dict) -> List[PolicyCookie]:
        """Xử lý cookie từ policy JSON"""
        pass

    @abstractmethod
    def process_actual_cookies(self, cookies: List[Dict]) -> List[ActualCookie]:
        """Xử lý cookie thực tế từ request"""
        pass
