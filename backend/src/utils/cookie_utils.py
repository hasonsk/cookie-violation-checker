import re
import base64
import email.utils
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

from schemas.cookie_schema import ActualCookie


def parse_cookie(raw: dict) -> Optional[ActualCookie]:
    """Parse cookie từ raw data với error handling tốt hơn"""
    try:
        expirationDate_str = raw.get("expirationDate")
        expirationDate = None

        if expirationDate_str and expirationDate_str != "Session":
            try:
                expirationDate = email.utils.parsedate_to_datetime(expirationDate_str)
            except Exception:
                # Thử parse các format khác
                try:
                    if isinstance(expirationDate_str, (int, float)):
                        expirationDate = datetime.fromtimestamp(expirationDate_str)
                    elif isinstance(expirationDate_str, str):
                        # Thử ISO format
                        expirationDate = datetime.fromisoformat(expirationDate_str.replace('Z', '+00:00'))
                except Exception:
                    pass

        return ActualCookie(
            name=raw.get("name", ""),
            value=raw.get("value", ""),
            domain=raw.get("domain", ""),
            expirationDate=expirationDate,
            path=raw.get("path", "/"),
            secure=raw.get("secure", False),
            httpOnly=raw.get("httpOnly", False),
            sameSite=raw.get("sameSite"),
        )
    except Exception as e:
        print(f"Error parsing cookie: {e}")
        return None


def parse_retention_to_days(retention_str: str) -> Optional[int]:
    """Chuyển đổi retention string thành số ngày với nhiều format hơn"""
    if not retention_str:
        return None

    retention_lower = retention_str.lower().strip()

    if 'session' in retention_lower or 'browser' in retention_lower:
        return 0

    # Parse các format phổ biến với regex tốt hơn
    patterns = [
        (r'(\d+(?:\.\d+)?)\s*year[s]?', 365),
        (r'(\d+(?:\.\d+)?)\s*month[s]?', 30),
        (r'(\d+(?:\.\d+)?)\s*week[s]?', 7),
        (r'(\d+(?:\.\d+)?)\s*day[s]?', 1),
        (r'(\d+(?:\.\d+)?)\s*hour[s]?', 1/24),
        (r'(\d+(?:\.\d+)?)\s*minute[s]?', 1/(24*60))
    ]

    for pattern, multiplier in patterns:
        match = re.search(pattern, retention_lower)
        if match:
            return int(float(match.group(1)) * multiplier)

    # Xử lý các case đặc biệt
    if 'permanent' in retention_lower or 'forever' in retention_lower:
        return 10000  # Số rất lớn để biểu thị permanent

    if 'short' in retention_lower:
        return 7  # Assume short-term = 1 week

    if 'long' in retention_lower:
        return 365  # Assume long-term = 1 year

    return None


def calculate_actual_retention_days(expirationDate: Optional[datetime]) -> Optional[int]:
    """Tính số ngày retention thực tế với timezone handling"""
    if not expirationDate:
        return 0  # Session cookie

    now = datetime.now()
    # Handle timezone-aware datetime
    if expirationDate.tzinfo and not now.tzinfo:
        now = now.replace(tzinfo=expirationDate.tzinfo)
    elif not expirationDate.tzinfo and now.tzinfo:
        expirationDate = expirationDate.replace(tzinfo=now.tzinfo)

    if expirationDate <= now:
        return 0

    delta = expirationDate - now
    return max(0, delta.days)


def is_third_party_domain(cookie_domain: str, main_domain: str) -> bool:
    """Kiểm tra domain có phải third-party không với logic cải thiện"""
    if not cookie_domain or not main_domain:
        return False

    cookie_domain_clean = cookie_domain.lstrip('.')
    main_domain_clean = main_domain.lstrip('.')

    # Same domain
    if cookie_domain_clean == main_domain_clean:
        return False

    # Subdomain of main domain
    if cookie_domain_clean.endswith('.' + main_domain_clean):
        return False

    # Main domain is subdomain of cookie domain (reverse case)
    if main_domain_clean.endswith('.' + cookie_domain_clean):
        return False

    return True


def analyze_cookie_data_collection(cookie: ActualCookie) -> bool:
    """Phân tích xem cookie có thu thập dữ liệu người dùng không"""
    if not cookie.value:
        return False

    user_data_indicators = [
        # User identifiers
        r'user[_-]?id', r'\buid\b', r'uuid', r'guid', r'customer[_-]?id',
        # Session indicators
        r'sess[_-]?id', r'session', r'\bsid\b', r'jsessionid',
        # Tracking indicators
        r'track', r'analytics', r'ga[0-9]', r'gtm', r'_utm', r'campaign',
        # Behavioral data
        r'visit', r'page[_-]?view', r'click', r'scroll', r'engagement',
        # Device/browser fingerprinting
        r'screen', r'resolution', r'browser', r'device', r'platform',
        # Location data
        r'geo', r'location', r'country', r'region', r'timezone',
        # Timestamp patterns
        r'\d{10,13}', r'\d{4}-\d{2}-\d{2}',
        # Authentication tokens
        r'token', r'auth', r'jwt', r'oauth'
    ]

    # Check cookie name
    for pattern in user_data_indicators:
        if re.search(pattern, cookie.name, re.IGNORECASE):
            return True

    # Check cookie value
    for pattern in user_data_indicators:
        if re.search(pattern, cookie.value, re.IGNORECASE):
            return True

    # Check if value looks like encoded data
    if len(cookie.value) > 20 and re.match(r'^[A-Za-z0-9+/]+={0,2}$', cookie.value):
        try:
            decoded = base64.b64decode(cookie.value, validate=True).decode('utf-8', errors='ignore')
            for pattern in user_data_indicators:
                if re.search(pattern, decoded, re.IGNORECASE):
                    return True
        except Exception:
            pass

    return False


def extract_main_domain(url: str) -> str:
    """Extract main domain from URL"""
    try:
        return urlparse(url).netloc
    except Exception:
        return ""


def calculate_semantic_similarity(text1: str, text2: str) -> float:
    """Tính độ tương đồng ngữ nghĩa với xử lý tốt hơn"""
    import difflib
    if not text1 or not text2:
        return 0.0
    return difflib.SequenceMatcher(None, text1.lower().strip(), text2.lower().strip()).ratio()
