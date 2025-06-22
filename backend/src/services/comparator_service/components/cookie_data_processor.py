from typing import Dict, List, Union
# Removed datetime import as it's no longer needed for conversion here

from src.schemas.cookie import PolicyCookie, ActualCookie
from src.services.comparator_service.interfaces.cookie_data_processor import ICookieDataProcessor

class CookieDataProcessor(ICookieDataProcessor):
    """Chuyên xử lý dữ liệu cookie - FUNCTIONAL COHESION"""

    def process_policy_cookies(self, policy_json: Dict) -> List[PolicyCookie]:
        """Chỉ làm 1 việc: chuyển đổi policy JSON thành PolicyCookie objects"""
        if not policy_json or "cookies" not in policy_json:
            return []

        return [PolicyCookie(**cookie_data) for cookie_data in policy_json["cookies"]]

    def process_actual_cookies(self, cookies: List[ActualCookie]) -> List[ActualCookie]:
        """
        Chuẩn hóa expirationDate của các ActualCookie objects.
        """
        for cookie in cookies:
            if cookie.expirationDate == 'Session':
                cookie.expirationDate = None
            # If it's already None or a string, keep it as is.
            # The schema now expects Optional[str], so no datetime conversion here.
        return cookies

    # _normalize_expiration_date is no longer needed as a separate method
    # since the logic is now directly in process_actual_cookies.
    # Removing it to keep the code clean.
