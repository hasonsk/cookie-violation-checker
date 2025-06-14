from typing import Dict, List
from datetime import datetime

from src.schemas.cookie import PolicyCookie, ActualCookie
from src.services.comparator_service.interfaces.cookie_data_processor import ICookieDataProcessor

class CookieDataProcessor(ICookieDataProcessor):
    """Chuyên xử lý dữ liệu cookie - FUNCTIONAL COHESION"""

    def process_policy_cookies(self, policy_json: Dict) -> List[PolicyCookie]:
        """Chỉ làm 1 việc: chuyển đổi policy JSON thành PolicyCookie objects"""
        if not policy_json or "cookies" not in policy_json:
            return []

        return [PolicyCookie(**cookie_data) for cookie_data in policy_json["cookies"]]

    def process_actual_cookies(self, cookies: List[Dict]) -> List[ActualCookie]:
        """Chỉ làm 1 việc: chuyển đổi cookie data thành ActualCookie objects"""
        processed_cookies = []

        for cookie_data in cookies:
            # Chuẩn hóa expirationDate
            cookie_data = self._normalize_expiration_date(cookie_data)
            processed_cookies.append(ActualCookie(**cookie_data))

        return processed_cookies

    def _normalize_expiration_date(self, cookie_data: Dict) -> Dict:
        """Helper method chỉ để chuẩn hóa expiration date"""
        if 'expirationDate' not in cookie_data:
            return cookie_data

        exp_date = cookie_data['expirationDate']

        if exp_date == 'Session' or exp_date is None:
            cookie_data['expirationDate'] = None
        elif not isinstance(exp_date, (datetime, type(None))):
            try:
                cookie_data['expirationDate'] = datetime.fromisoformat(
                    exp_date.replace('Z', '+00:00')
                )
            except (ValueError, TypeError):
                cookie_data['expirationDate'] = None

        return cookie_data
