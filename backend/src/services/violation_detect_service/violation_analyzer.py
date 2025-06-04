import json
import re
from typing import Dict, List, Any

from schemas.cookie_schema import PolicyCookie, PolicyCookieList, ActualCookie, ComplianceIssue
from configs.violation_config import KNOWN_AD_TRACKERS
from utils.cookie_utils import (
    parse_cookie, parse_retention_to_days, calculate_actual_retention_days,
    is_third_party_domain, analyze_cookie_data_collection,
    calculate_semantic_similarity
)

class ViolationAnalyzer:
    def __init__(self, known_ad_trackers=KNOWN_AD_TRACKERS):
        self.known_ad_trackers = known_ad_trackers

        # Mapping domain patterns to likely purposes
        self.domain_purpose_mapping = {
            'analytics': ['google-analytics.com', 'googletagmanager.com', 'hotjar.com', 'segment.com', 'mixpanel.com'],
            'advertising': ['doubleclick.net', 'googlesyndication.com', 'amazon-adsystem.com'],
            'social': ['facebook.com', 'connect.facebook.net', 'twitter.com', 'linkedin.com'],
            'support': ['intercom.io', 'zendesk.com'],
            'media': ['youtube.com', 'googlevideo.com']
        }

    def parse_policy_data(self, policy_json: str) -> List[PolicyCookieList]:
        """Parse dữ liệu policy từ JSON với validation tốt hơn"""
        try:
            if isinstance(policy_json, str):
                data = json.loads(policy_json)
            else:
                data = policy_json

            cookies = []
            for cookie_data in data['cookies']:
                cookies.append(PolicyCookieList(
                    cookie_name=cookie_data.get('cookie_name', ''),
                    declared_purpose=cookie_data.get('declared_purpose', ''),
                    declared_retention=cookie_data.get('declared_retention', ''),
                    declared_third_parties=cookie_data.get('declared_third_parties', []),
                    declared_description=cookie_data.get('declared_description', '')
                ))
            return cookies
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Invalid JSON format: {e}")

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

    def infer_cookie_purpose(self, cookie: ActualCookie, main_domain: str) -> str:
        """Suy luận mục đích của cookie với logic cải thiện"""
        name_lower = cookie.name.lower()
        value_lower = cookie.value.lower() if cookie.value else ""
        domain_lower = cookie.domain.lower()

        # Authentication và session (highest priority)
        auth_patterns = [
            r'session', r'auth', r'login', r'token', r'csrf', r'jwt',
            r'user[_-]?id', r'account', r'remember', r'signin'
        ]

        for pattern in auth_patterns:
            if re.search(pattern, name_lower) or re.search(pattern, value_lower):
                return "Authentication/Session Management"

        # Analytics và tracking
        analytics_patterns = [
            r'analytics?', r'ga[0-9]?', r'gtm', r'track', r'pixel',
            r'_utm', r'campaign', r'source', r'medium', r'visitor'
        ]

        for pattern in analytics_patterns:
            if re.search(pattern, name_lower) or re.search(pattern, value_lower):
                return "Analytics/Tracking"

        # Advertising
        ad_patterns = [
            r'ad[sv]?', r'marketing', r'retarget', r'audience',
            r'conversion', r'attribution', r'affiliate', r'doubleclick'
        ]

        for pattern in ad_patterns:
            if re.search(pattern, name_lower) or re.search(pattern, value_lower):
                return "Advertising/Marketing"

        # Functional cookies
        functional_patterns = [
            r'preference', r'setting', r'language', r'currency',
            r'theme', r'layout', r'cart', r'wishlist', r'config'
        ]

        for pattern in functional_patterns:
            if re.search(pattern, name_lower) or re.search(pattern, value_lower):
                return "Functional/Preferences"

        # Performance cookies
        performance_patterns = [
            r'performance', r'speed', r'load', r'cache',
            r'cdn', r'optimization', r'bandwidth'
        ]

        for pattern in performance_patterns:
            if re.search(pattern, name_lower) or re.search(pattern, value_lower):
                return "Performance/Optimization"

        # Analyze based on domain
        if is_third_party_domain(cookie.domain, main_domain):
            domain_purpose = self.infer_third_party_purpose_from_domain(cookie.domain)
            if domain_purpose != "Unknown Third-party":
                return domain_purpose

        # Analyze based on retention
        retention_days = calculate_actual_retention_days(cookie.expirationDate)
        if retention_days is not None:
            if retention_days == 0:
                return "Session Management"
            elif retention_days <= 7:
                return "Short-term Functional"
            elif retention_days <= 90:
                return "User Preferences/Analytics"
            else:
                return "Long-term Tracking/Profiling"

        return "Unknown/Unclassified"

    def analyze_specific_issues(self, policy_cookies: List[PolicyCookie],
                              actual_cookies: List[ActualCookie],
                              main_domain: str) -> List[ComplianceIssue]:
        """Phân tích các vấn đề specific compliance"""
        issues = []
        policy_map = {cookie.cookie_name: cookie for cookie in policy_cookies}

        for actual_cookie in actual_cookies:
            policy_cookie = policy_map.get(actual_cookie.name)
            if not policy_cookie:
                continue

            # Issue 1: Session cookie nhưng persist > 24h
            if (policy_cookie.declared_retention.lower() == 'session' and
                actual_cookie.expirationDate and
                calculate_actual_retention_days(actual_cookie.expirationDate) > 1):

                issues.append(ComplianceIssue(
                    issue_id=1,
                    category="Specific",
                    type="Retention",
                    description="Cookie is declared as 'session' but persists longer than 24 hours",
                    severity="Medium",
                    cookie_name=actual_cookie.name,
                    details={
                        "declared": "session",
                        "actual_days": calculate_actual_retention_days(actual_cookie.expirationDate)
                    }
                ))

            # Issue 2: Actual expiration exceeds declared by > 30%
            declared_days = parse_retention_to_days(policy_cookie.declared_retention)
            actual_days = calculate_actual_retention_days(actual_cookie.expirationDate)

            if declared_days and actual_days and declared_days > 0:
                percentage_diff = ((actual_days - declared_days) / declared_days) * 100
                if percentage_diff > 30:
                    issues.append(ComplianceIssue(
                        issue_id=2,
                        category="Specific",
                        type="Retention",
                        description="Actual expiration exceeds declared duration by more than 30%",
                        severity="High",
                        cookie_name=actual_cookie.name,
                        details={
                            "declared_days": declared_days,
                            "actual_days": actual_days,
                            "percentage_diff": round(percentage_diff, 2)
                        }
                    ))

            # Additional specific issues implementation continues...
            # (Keeping the original logic but organized)

        return issues

    def analyze_general_issues(self, policy_cookies: List[PolicyCookieList],
                             actual_cookies: List[ActualCookie],
                             main_domain: str) -> List[ComplianceIssue]:
        """Phân tích các vấn đề general compliance"""
        issues = []

        # Lấy danh sách purposes từ policy
        declared_purposes = list(set(cookie.declared_purpose for cookie in policy_cookies if cookie.declared_purpose))
        standard_purposes = ["Strictly Necessary", "Functionality", "Analytical", "Targeting", "Performance", "Social Sharing"]

        for actual_cookie in actual_cookies:
            # Issue 8: Không có purpose phù hợp
            inferred_purpose = self.infer_cookie_purpose(actual_cookie, main_domain)

            # Tìm purpose tương tự nhất
            max_similarity = 0
            best_match = None

            for purpose in declared_purposes + standard_purposes:
                similarity = calculate_semantic_similarity(inferred_purpose, purpose)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = purpose

            # Nếu không tìm thấy purpose tương tự trong policy
            if best_match not in declared_purposes and max_similarity < 0.3:
                issues.append(ComplianceIssue(
                    issue_id=8,
                    category="General",
                    type="Purpose",
                    description="Cookie purpose shows no clear alignment with declared policy purposes",
                    severity="Medium",
                    cookie_name=actual_cookie.name,
                    details={
                        "inferred_purpose": inferred_purpose,
                        "best_match": best_match,
                        "similarity_score": round(max_similarity, 3),
                        "declared_purposes": declared_purposes
                    }
                ))

        return issues

    def analyze_undefined_issues(self, policy_cookies: List[PolicyCookieList],
                               actual_cookies: List[ActualCookie],
                               main_domain: str) -> List[ComplianceIssue]:
        """Phân tích các vấn đề undefined compliance"""
        issues = []
        declared_names = {cookie.cookie_name for cookie in policy_cookies}

        for actual_cookie in actual_cookies:
            if actual_cookie.name not in declared_names:
                # Issue 11: Cookie thu thập dữ liệu nhưng không có trong policy
                collects_data = analyze_cookie_data_collection(actual_cookie)
                is_third_party = is_third_party_domain(actual_cookie.domain, main_domain)
                persists_long = (
                    calculate_actual_retention_days(actual_cookie.expirationDate) and
                    calculate_actual_retention_days(actual_cookie.expirationDate) > 1
                )

                if collects_data and (is_third_party or persists_long):
                    inferred_purpose = self.infer_cookie_purpose(actual_cookie, main_domain)

                    issues.append(ComplianceIssue(
                        issue_id=11,
                        category="Undefined",
                        type="Purpose",
                        description="Undeclared cookie collects user data and persists or transmits to third-party",
                        severity="High",
                        cookie_name=actual_cookie.name,
                        details={
                            "collects_user_data": collects_data,
                            "is_third_party": is_third_party,
                            "persists_long": persists_long,
                            "inferred_purpose": inferred_purpose,
                            "retention_days": calculate_actual_retention_days(actual_cookie.expirationDate)
                        }
                    ))

        return issues

    def analyze_compliance(self, policy_json: PolicyCookieList, actual_cookies: List[ActualCookie],
                          main_domain: str) -> Dict[str, Any]:
        """Phân tích toàn bộ compliance với error handling tốt hơn"""
        try:
            policy_cookies = policy_json.cookies
            actual_cookies = [parse_cookie(c) for c in actual_cookies]

            specific_issues = self.analyze_specific_issues(policy_cookies, actual_cookies, main_domain)
            general_issues = self.analyze_general_issues(policy_cookies, actual_cookies, main_domain)
            undefined_issues = self.analyze_undefined_issues(policy_cookies, actual_cookies, main_domain)

            all_issues = specific_issues + general_issues + undefined_issues

            # Tính toán thống kê
            severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
            category_counts = {"Specific": 0, "General": 0, "Undefined": 0}
            type_counts = {}

            for issue in all_issues:
                severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
                category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
                type_counts[issue.type] = type_counts.get(issue.type, 0) + 1

            # Tính compliance score dựa trên severity
            severity_weights = {"Critical": 20, "High": 10, "Medium": 5, "Low": 2}
            penalty = sum(severity_weights.get(issue.severity, 5) for issue in all_issues)
            compliance_score = max(0, 100 - penalty)

            return {
                "total_issues": len(all_issues),
                "issues": [
                    {
                        "issue_id": issue.issue_id,
                        "category": issue.category,
                        "type": issue.type,
                        "description": issue.description,
                        "severity": issue.severity,
                        "cookie_name": issue.cookie_name,
                        "details": issue.details
                    }
                    for issue in sorted(all_issues, key=lambda x: (
                        ["Critical", "High", "Medium", "Low"].index(x.severity),
                        x.category,
                        x.cookie_name
                    ))
                ],
                "statistics": {
                    "by_severity": severity_counts,
                    "by_category": category_counts,
                    "by_type": type_counts
                },
                "policy_cookies_count": len(policy_cookies),
                "actual_cookies_count": len(actual_cookies),
                "compliance_score": compliance_score,
                "summary": {
                    "critical_issues": severity_counts["Critical"],
                    "high_issues": severity_counts["High"],
                    "undeclared_cookies": [c.name for c in actual_cookies
                                             if c.name not in {pc.cookie_name for pc in policy_cookies}],
                    "declared_cookies": [c.declared_name for c in policy_cookies],
                    "third_party_cookies": [c.name for c in actual_cookies
                                              if is_third_party_domain(c.domain, main_domain)],
                    "long_term_cookies": [c.name for c in actual_cookies
                                             if calculate_actual_retention_days(c.expirationDate) and
                                                calculate_actual_retention_days(c.expirationDate) > 365]
                }
            }

        except Exception as e:
            print("Error: ", e)
            return {
                "error": str(e),
            }
