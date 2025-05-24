import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class CookiePattern:
    """Định nghĩa pattern cho từng loại cookie"""
    name_patterns: List[str]
    value_patterns: List[str] = None
    domain_patterns: List[str] = None
    path_patterns: List[str] = None
    priority: int = 0  # Độ ưu tiên, số càng cao càng ưu tiên

    def __post_init__(self):
        if self.value_patterns is None:
            self.value_patterns = []
        if self.domain_patterns is None:
            self.domain_patterns = []
        if self.path_patterns is None:
            self.path_patterns = []

class ImprovedCookiePurposeInferencer:

    def __init__(self):
        # Định nghĩa patterns cho từng loại cookie với độ ưu tiên
        self.cookie_patterns = {
            "Strictly Necessary": CookiePattern(
                name_patterns=[
                    r'^(csrf|xsrf)[_-]?token$',
                    r'^session[_-]?id$',
                    r'^jsessionid$',
                    r'^phpsessid$',
                    r'^asp\.net[_-]?sessionid$',
                    r'^connect\.sid$',
                    r'^express[_-]?session$',
                    r'^laravel[_-]?session$',
                    r'^django[_-]?sessionid$',
                    r'^security[_-]?token$',
                    r'^anti[_-]?forgery[_-]?token$',
                    r'^__cfduid$',  # Cloudflare security
                    r'^__cf_bm$',   # Cloudflare bot management
                    r'^incap_ses_',  # Incapsula security
                    r'^visid_incap_',  # Incapsula security
                    r'^load[_-]?balancer',
                    r'^server[_-]?affinity',
                    r'^sticky[_-]?session',
                ],
                value_patterns=[
                    r'^[a-f0-9]{32,}$',  # Hash-like values for security tokens
                ],
                priority=10
            ),

            "Authentication/Session Management": CookiePattern(
                name_patterns=[
                    r'session(?!_utm)',  # session nhưng không phải session_utm
                    r'auth(?!_ga)',      # auth nhưng không phải auth_ga
                    r'login',
                    r'token(?!_ga)',
                    r'user[_-]?id',
                    r'account[_-]?id',
                    r'remember[_-]?me',
                    r'remember[_-]?user',
                    r'logged[_-]?in',
                    r'access[_-]?token',
                    r'refresh[_-]?token',
                    r'oauth[_-]?token',
                    r'jwt[_-]?token',
                    r'bearer[_-]?token',
                ],
                priority=8
            ),

            "Analytics/Tracking": CookiePattern(
                name_patterns=[
                    r'^_ga',           # Google Analytics
                    r'^_gid',          # Google Analytics
                    r'^_gat',          # Google Analytics
                    r'^_gtm',          # Google Tag Manager
                    r'^_dc_gtm_',      # Google Tag Manager
                    r'analytics?',
                    r'track(?:ing)?',
                    r'pixel',
                    r'_utm_',
                    r'campaign',
                    r'source',
                    r'medium',
                    r'_fbp',           # Facebook Pixel
                    r'_fbc',           # Facebook Pixel
                    r'__utma',         # Google Analytics (Legacy)
                    r'__utmb',         # Google Analytics (Legacy)
                    r'__utmc',         # Google Analytics (Legacy)
                    r'__utmz',         # Google Analytics (Legacy)
                    r'_adobe_',        # Adobe Analytics
                    r'_omappvp',       # Adobe Analytics
                    r'_hjid',          # Hotjar
                    r'_hjIncludedInSample',  # Hotjar
                ],
                domain_patterns=[
                    r'googleanalytics\.com',
                    r'google-analytics\.com',
                    r'facebook\.com',
                    r'hotjar\.com',
                    r'adobe\.com',
                ],
                priority=6
            ),

            "Advertising/Marketing": CookiePattern(
                name_patterns=[
                    r'ad[sv]?[_-]?',
                    r'marketing',
                    r'retarget',
                    r'audience',
                    r'conversion',
                    r'attribution',
                    r'affiliate',
                    r'doubleclick',
                    r'_gcl_',          # Google Click Identifier
                    r'_gac_',          # Google Ads Conversion
                    r'personalization_id',  # Twitter
                    r'_pinterest_',    # Pinterest
                    r'_linkedin_',     # LinkedIn
                    r'_ym_',          # Yandex Metrica
                ],
                domain_patterns=[
                    r'doubleclick\.net',
                    r'googlesyndication\.com',
                    r'facebook\.com',
                    r'twitter\.com',
                    r'linkedin\.com',
                    r'pinterest\.com',
                ],
                priority=5
            ),

            "Functional/Preferences": CookiePattern(
                name_patterns=[
                    r'preference[s]?',
                    r'setting[s]?',
                    r'language',
                    r'locale',
                    r'currency',
                    r'theme',
                    r'layout',
                    r'cart',
                    r'wishlist',
                    r'favorite[s]?',
                    r'bookmark[s]?',
                    r'recently[_-]?viewed',
                    r'filter[s]?',
                    r'sort[_-]?order',
                    r'view[_-]?mode',
                    r'timezone',
                ],
                priority=4
            ),

            "Performance/Optimization": CookiePattern(
                name_patterns=[
                    r'performance',
                    r'speed',
                    r'load[_-]?',
                    r'cache',
                    r'cdn',
                    r'optimization',
                    r'compress',
                    r'minif',
                ],
                priority=3
            )
        }

        # Compiled regex patterns for better performance
        self._compiled_patterns = {}
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile tất cả regex patterns để tăng hiệu suất"""
        for purpose, pattern_obj in self.cookie_patterns.items():
            self._compiled_patterns[purpose] = {
                'name': [re.compile(p, re.IGNORECASE) for p in pattern_obj.name_patterns],
                'value': [re.compile(p, re.IGNORECASE) for p in pattern_obj.value_patterns],
                'domain': [re.compile(p, re.IGNORECASE) for p in pattern_obj.domain_patterns],
                'path': [re.compile(p, re.IGNORECASE) for p in pattern_obj.path_patterns],
                'priority': pattern_obj.priority
            }

    def _check_security_indicators(self, cookie) -> bool:
        """Kiểm tra các chỉ số bảo mật của cookie"""
        security_flags = 0

        # Secure flag
        if hasattr(cookie, 'secure') and cookie.secure:
            security_flags += 1

        # HttpOnly flag
        if hasattr(cookie, 'httponly') and cookie.httponly:
            security_flags += 1

        # SameSite attribute
        if hasattr(cookie, 'samesite') and cookie.samesite:
            security_flags += 1

        # Path restriction (more specific paths are more likely to be functional)
        if hasattr(cookie, 'path') and cookie.path and cookie.path != '/':
            security_flags += 0.5

        return security_flags >= 2  # Có ít nhất 2 chỉ số bảo mật

    def _analyze_cookie_value(self, value: str) -> Dict[str, float]:
        """Phân tích giá trị cookie để xác định loại"""
        if not value:
            return {}

        analysis = {}

        # JWT token pattern
        if re.match(r'^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$', value):
            analysis['jwt_token'] = 0.9

        # Hash-like values (security tokens, session IDs)
        if re.match(r'^[a-f0-9]{32,}$', value.lower()):
            analysis['hash_token'] = 0.8

        # UUID pattern
        if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', value.lower()):
            analysis['uuid'] = 0.8

        # Base64 encoded data
        if re.match(r'^[A-Za-z0-9+/=]+$', value) and len(value) % 4 == 0:
            analysis['base64'] = 0.6

        # Timestamp values
        if re.match(r'^\d{10,13}$', value):  # Unix timestamp
            analysis['timestamp'] = 0.5

        return analysis

    def _calculate_confidence_score(self, matches: List[Tuple[str, float]]) -> Dict[str, float]:
        """Tính toán độ tin cậy cho mỗi loại cookie"""
        confidence_scores = {}

        for purpose, score in matches:
            if purpose not in confidence_scores:
                confidence_scores[purpose] = 0
            confidence_scores[purpose] += score

        # Normalize scores
        if confidence_scores:
            max_score = max(confidence_scores.values())
            for purpose in confidence_scores:
                confidence_scores[purpose] = min(confidence_scores[purpose] / max_score, 1.0)

        return confidence_scores

    def infer_cookie_purpose(self, cookie) -> Dict[str, any]:
        """
        Suy luận mục đích của cookie với độ tin cậy và thông tin chi tiết

        Returns:
            Dict chứa purpose, confidence, details, và flags
        """
        name_lower = cookie.name.lower()
        value_lower = cookie.value.lower() if cookie.value else ""
        domain_lower = cookie.domain.lower() if hasattr(cookie, 'domain') and cookie.domain else ""
        path = cookie.path if hasattr(cookie, 'path') and cookie.path else "/"

        matches = []
        details = {
            'matched_patterns': [],
            'security_indicators': self._check_security_indicators(cookie),
            'value_analysis': self._analyze_cookie_value(cookie.value) if cookie.value else {},
            'flags': {
                'secure': getattr(cookie, 'secure', False),
                'httponly': getattr(cookie, 'httponly', False),
                'samesite': getattr(cookie, 'samesite', None),
            }
        }

        # Kiểm tra từng loại cookie theo thứ tự ưu tiên
        for purpose, compiled_patterns in sorted(
            self._compiled_patterns.items(),
            key=lambda x: x[1]['priority'],
            reverse=True
        ):
            match_score = 0
            matched_patterns = []

            # Kiểm tra name patterns
            for pattern in compiled_patterns['name']:
                if pattern.search(name_lower):
                    match_score += 1.0
                    matched_patterns.append(f"name:{pattern.pattern}")

            # Kiểm tra value patterns
            for pattern in compiled_patterns['value']:
                if pattern.search(value_lower):
                    match_score += 0.8
                    matched_patterns.append(f"value:{pattern.pattern}")

            # Kiểm tra domain patterns
            for pattern in compiled_patterns['domain']:
                if pattern.search(domain_lower):
                    match_score += 0.6
                    matched_patterns.append(f"domain:{pattern.pattern}")

            # Bonus điểm cho Strictly Necessary nếu có security indicators
            if purpose == "Strictly Necessary" and details['security_indicators']:
                match_score += 0.5
                matched_patterns.append("security_indicators")

            # Bonus điểm dựa trên value analysis
            if details['value_analysis']:
                if purpose == "Strictly Necessary" and ('hash_token' in details['value_analysis'] or 'jwt_token' in details['value_analysis']):
                    match_score += 0.3
                elif purpose == "Authentication/Session Management" and 'uuid' in details['value_analysis']:
                    match_score += 0.2

            if match_score > 0:
                matches.append((purpose, match_score))
                details['matched_patterns'].extend(matched_patterns)

        # Tính toán confidence scores
        confidence_scores = self._calculate_confidence_score(matches)

        # Xác định purpose chính
        if confidence_scores:
            primary_purpose = max(confidence_scores.items(), key=lambda x: x[1])
            result_purpose = primary_purpose[0]
            result_confidence = primary_purpose[1]
        else:
            result_purpose = "Unknown"
            result_confidence = 0.0

        return {
            'purpose': result_purpose,
            'confidence': result_confidence,
            'all_matches': confidence_scores,
            'details': details
        }

# Ví dụ sử dụng
if __name__ == "__main__":
    from collections import namedtuple

    # Mock cookie object
    Cookie = namedtuple('Cookie', ['name', 'value', 'domain', 'path', 'secure', 'httponly', 'samesite'])

    inferencer = ImprovedCookiePurposeInferencer()

    # Test cases
    test_cookies = [
        Cookie("csrf_token", "abc123def456", "example.com", "/", True, True, "Strict"),
        Cookie("_ga", "GA1.2.123456789.987654321", "example.com", "/", False, False, None),
        Cookie("session_id", "uuid-1234-5678-9012", "example.com", "/admin", True, True, "Lax"),
        Cookie("ad_preferences", "targeting_data", "ads.example.com", "/", False, False, None),
        Cookie("theme", "dark", "example.com", "/", False, False, None),
    ]

    for cookie in test_cookies:
        result = inferencer.infer_cookie_purpose(cookie)
        print(f"\nCookie: {cookie.name}")
        print(f"Purpose: {result['purpose']} (Confidence: {result['confidence']:.2f})")
        print(f"All matches: {result['all_matches']}")
        print(f"Security indicators: {result['details']['security_indicators']}")
