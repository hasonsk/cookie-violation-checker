import difflib
from typing import Dict, List


class DomainAnalyzer:
    """Utility class để phân tích domain và purpose"""

    def __init__(self):
        self.known_ad_trackers = [
            'doubleclick.net', 'google-analytics.com', 'googletagmanager.com',
            'facebook.com', 'connect.facebook.net', 'twitter.com', 'linkedin.com',
            'amazon-adsystem.com', 'googlesyndication.com', 'adsystem.amazon.com',
            'youtube.com', 'googlevideo.com', 'hotjar.com', 'segment.com',
            'mixpanel.com', 'intercom.io', 'zendesk.com'
        ]

        # Mapping domain patterns to likely purposes
        self.domain_purpose_mapping = {
            'analytics': ['google-analytics.com', 'googletagmanager.com', 'hotjar.com', 'segment.com', 'mixpanel.com'],
            'advertising': ['doubleclick.net', 'googlesyndication.com', 'amazon-adsystem.com'],
            'social': ['facebook.com', 'connect.facebook.net', 'twitter.com', 'linkedin.com'],
            'support': ['intercom.io', 'zendesk.com'],
            'media': ['youtube.com', 'googlevideo.com']
        }

    def is_third_party_domain(self, cookie_domain: str, main_domain: str) -> bool:
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

    def is_known_ad_tracker(self, domain: str) -> bool:
        """Kiểm tra domain có phải ad tracker không"""
        if not domain:
            return False

        domain_lower = domain.lower()
        return any(tracker in domain_lower for tracker in self.known_ad_trackers)

    def infer_third_party_purpose_from_domain(self, domain: str) -> str:
        """Suy luận mục đích third-party từ domain"""
        if not domain:
            return "Unknown"

        domain_lower = domain.lower()

        for purpose, domains in self.domain_purpose_mapping.items():
            if any(known_domain in domain_lower for known_domain in domains):
                return purpose.title()

        if self.is_known_ad_tracker(domain):
            return "Advertising/Tracking"

        return "Unknown Third-party"

    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Tính độ tương đồng ngữ nghĩa với xử lý tốt hơn"""
        if not text1 or not text2:
            return 0.0
        return difflib.SequenceMatcher(None, text1.lower().strip(), text2.lower().strip()).ratio()
