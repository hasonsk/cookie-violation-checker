import json
import re
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import difflib
from dataclasses import dataclass

@dataclass
class PolicyCookie:
    """Cấu trúc cookie được khai báo trong policy"""
    cookie_name: str
    declared_purpose: str
    declared_retention: str
    declared_third_parties: List[str]
    declared_description: str

@dataclass
class ActualCookie:
    """Cấu trúc cookie thu thập được thực tế"""
    name: str
    value: str
    domain: str
    expires: Optional[datetime]
    secure: bool
    http_only: bool
    same_site: Optional[str]
    third_party_requests: List[str]

@dataclass
class ComplianceIssue:
    """Cấu trúc vấn đề compliance được phát hiện"""
    issue_id: int
    category: str
    type: str
    description: str
    severity: str
    cookie_name: str
    details: Dict[str, Any]

class ViolationAnalyzer:
    """Module phân tích compliance giữa cookie policy và thực tế"""

    def __init__(self):
        self.known_ad_trackers = [
            'doubleclick.net', 'google-analytics.com', 'facebook.com',
            'twitter.com', 'linkedin.com', 'amazon-adsystem.com'
        ]

    def parse_policy_data(self, policy_json: str) -> List[PolicyCookie]:
        """Parse dữ liệu policy từ JSON"""
        try:
            data = json.loads(policy_json)
            cookies = []
            for cookie_data in data.get('cookies', []):
                cookies.append(PolicyCookie(
                    cookie_name=cookie_data.get('cookie_name', ''),
                    declared_purpose=cookie_data.get('declared_purpose', ''),
                    declared_retention=cookie_data.get('declared_retention', ''),
                    declared_third_parties=cookie_data.get('declared_third_parties', []),
                    declared_description=cookie_data.get('declared_description', '')
                ))
            return cookies
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

    def parse_retention_to_days(self, retention_str: str) -> Optional[int]:
        """Chuyển đổi retention string thành số ngày"""
        if not retention_str:
            return None

        retention_lower = retention_str.lower()

        if 'session' in retention_lower:
            return 0

        # Parse các format phổ biến
        patterns = [
            (r'(\d+)\s*year', 365),
            (r'(\d+)\s*month', 30),
            (r'(\d+)\s*week', 7),
            (r'(\d+)\s*day', 1),
            (r'(\d+)\s*hour', 1/24)
        ]

        for pattern, multiplier in patterns:
            match = re.search(pattern, retention_lower)
            if match:
                return int(float(match.group(1)) * multiplier)

        return None

    def calculate_actual_retention_days(self, expires: Optional[datetime]) -> Optional[int]:
        """Tính số ngày retention thực tế"""
        if not expires:
            return 0  # Session cookie

        now = datetime.now()
        if expires <= now:
            return 0

        delta = expires - now
        return delta.days

    def is_third_party_domain(self, domain: str, main_domain: str) -> bool:
        """Kiểm tra domain có phải third-party không"""
        domain_clean = domain.lstrip('.')
        main_domain_clean = main_domain.lstrip('.')

        return not (domain_clean == main_domain_clean or
                   domain_clean.endswith('.' + main_domain_clean))

    def is_known_ad_tracker(self, domain: str) -> bool:
        """Kiểm tra domain có phải ad tracker không"""
        for tracker in self.known_ad_trackers:
            if tracker in domain:
                return True
        return False

    def _analyzes_cookie_data_collection(self, cookie: 'ActualCookie') -> bool:
        """Phân tích xem cookie có thu thập dữ liệu người dùng không"""
        if not cookie.value:
            return False

        user_data_indicators = [
            # User identifiers
            r'user[_-]?id', r'uid', r'uuid', r'guid',
            # Session indicators
            r'sess[_-]?id', r'session', r'sid',
            # Tracking indicators
            r'track', r'analytics', r'ga[0-9]', r'gtm',
            # Behavioral data
            r'visit', r'page[_-]?view', r'click', r'scroll',
            # Device/browser fingerprinting
            r'screen', r'resolution', r'browser', r'device',
            # Location data
            r'geo', r'location', r'country', r'region',
            # Timestamp patterns (Unix timestamp, ISO format)
            r'\d{10,13}', r'\d{4}-\d{2}-\d{2}',
            # Base64 encoded data
            r'^[A-Za-z0-9+/]+={0,2}$'
        ]

        value = cookie.value

                # 1. Kiểm tra tên cookie
        for pattern in user_data_indicators:
            if re.search(pattern, cookie.name, re.IGNORECASE):
                return True

        # 2. Kiểm tra giá trị cookie
        for pattern in user_data_indicators:
            if re.search(pattern, value, re.IGNORECASE):
                return True

        # 3. Nếu có thể, thử giải mã base64 để kiểm tra dữ liệu mã hóa
        try:
            decoded = base64.b64decode(value, validate=True).decode('utf-8', errors='ignore')
            for pattern in user_data_indicators:
                if re.search(pattern, decoded, re.IGNORECASE):
                    return True
        except Exception:
            pass  # Không phải base64 hợp lệ hoặc không thể giải mã

        return False

    def _get_data_collection_indicators(self, cookie: 'ActualCookie') -> List[str]:
        """Lấy danh sách các chỉ số cho thấy cookie thu thập dữ liệu"""
        indicators = []

        name_lower = cookie.name.lower()
        value_lower = cookie.value.lower() if cookie.value else ""

        # Patterns để detect
        indicator_patterns = {
            "User Identifier": [r'user[_-]?id', r'uid', r'uuid', r'guid'],
            "Session Data": [r'sess[_-]?id', r'session', r'sid'],
            "Tracking Data": [r'track', r'analytics', r'ga[0-9]', r'gtm'],
            "Behavioral Data": [r'visit', r'page[_-]?view', r'click', r'scroll'],
            "Device Data": [r'screen', r'resolution', r'browser', r'device'],
            "Location Data": [r'geo', r'location', r'country', r'region'],
            "Timestamp": [r'\d{10,13}', r'\d{4}-\d{2}-\d{2}'],
            "Encoded Data": [r'^[A-Za-z0-9+/]+={0,2}$'],
        }

        # 1. Kiểm tra trong tên cookie
        for label, patterns in indicator_patterns.items():
            for pattern in patterns:
                if re.search(pattern, name_lower, re.IGNORECASE):
                    indicators.append(label)
                    break  # Chỉ cần một pattern là đủ để đánh dấu

        # 2. Kiểm tra trong giá trị cookie
        for label, patterns in indicator_patterns.items():
            for pattern in patterns:
                if re.search(pattern, value_lower, re.IGNORECASE):
                    indicators.append(label)
                    break

        # 3. Giải mã base64 nếu có thể, rồi kiểm tra
        try:
            decoded_value = base64.b64decode(cookie.value, validate=True).decode('utf-8', errors='ignore')
            decoded_lower = decoded_value.lower()
            for label, patterns in indicator_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, decoded_lower, re.IGNORECASE):
                        indicators.append(f"{label} (from base64)")
                        break
        except Exception:
            pass  # Không phải dữ liệu base64 hoặc giải mã lỗi

        # Loại bỏ trùng lặp
        return list(set(indicators))

    def _infer_cookie_purpose(self, cookie: ActualCookie) -> str:
        """Suy luận mục đích của cookie dựa trên phân tích nội dung"""
        name_lower = cookie.name.lower()
        value_lower = cookie.value.lower() if cookie.value else ""
        domain = cookie.domain.lower()

        # Analytics và tracking
        analytics_patterns = [
            r'analytics?', r'ga[0-9]?', r'gtm', r'track', r'pixel',
            r'_utm', r'campaign', r'source', r'medium'
        ]

        # Authentication và session
        auth_patterns = [
            r'session', r'auth', r'login', r'token', r'csrf',
            r'user[_-]?id', r'account', r'remember'
        ]

        # Advertising và marketing
        ad_patterns = [
            r'ad[sv]?', r'marketing', r'retarget', r'audience',
            r'conversion', r'attribution', r'affiliate'
        ]

        # Functional cookies
        functional_patterns = [
            r'preference', r'setting', r'language', r'currency',
            r'theme', r'layout', r'cart', r'wishlist'
        ]

        # Performance cookies
        performance_patterns = [
            r'performance', r'speed', r'load', r'cache',
            r'cdn', r'optimization'
        ]

        # Kiểm tra theo thứ tự ưu tiên
        pattern_groups = [
            (auth_patterns, "Authentication/Session Management"),
            (analytics_patterns, "Analytics/Tracking"),
            (ad_patterns, "Advertising/Marketing"),
            (functional_patterns, "Functional/Preferences"),
            (performance_patterns, "Performance/Optimization")
        ]

        for patterns, purpose in pattern_groups:
            for pattern in patterns:
                if (re.search(pattern, name_lower) or
                    re.search(pattern, value_lower)):
                    return purpose

        # Phân tích dựa trên domain
        # if self.is_known_ad_tracker(domain):
        #     return "Advertising/Tracking"

        # Phân tích dựa trên third-party requests
        # if cookie.third_party_requests:
        #     ad_domains = [d for d in cookie.third_party_requests if self.is_known_ad_tracker(d)]
        #     if ad_domains:
        #         return "Advertising/Cross-site Tracking"

        # Phân tích dựa trên retention
        # retention_days = self.calculate_actual_retention_days(cookie.expires)
        # if retention_days:
        #     if retention_days == 0:
        #         return "Session Management"
        #     elif retention_days <= 7:
        #         return "Short-term Functional"
        #     elif retention_days <= 90:
        #         return "User Preferences/Analytics"
        #     else:
        #         return "Long-term Tracking/Profiling"

        return "Unknown/Unclassified"

    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Tính độ tương đồng ngữ nghĩa đơn giản"""
        # Sử dụng difflib để tính similarity
        return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def analyze_specific_issues(self, policy_cookies: List[PolicyCookie],
                              actual_cookies: List[ActualCookie],
                              main_domain: str) -> List[ComplianceIssue]:
        """Phân tích các vấn đề specific compliance"""
        issues = []

        # Tạo mapping cookie name -> policy
        policy_map = {cookie.cookie_name: cookie for cookie in policy_cookies}

        for actual_cookie in actual_cookies:
            policy_cookie = policy_map.get(actual_cookie.name)
            if not policy_cookie:
                # Cần xử lý đối với các cookie không có trong khai báo như là cookie undefined --> Xử lý tuong tự như với genneral dựa trên các cookie đã khai báo
                continue


            # Issue 1: Session cookie nhưng persist > 24h   ---> OK
            # if (policy_cookie.declared_retention.lower() == 'session' and
            #     actual_cookie.expires and
            #     self.calculate_actual_retention_days(actual_cookie.expires) > 1):

            #     issues.append(ComplianceIssue(
            #         issue_id=1,
            #         category="Specific",
            #         type="Retention",
            #         description="Cookie is declared as 'session' but persists longer than 24 hours",
            #         severity="Medium",
            #         cookie_name=actual_cookie.name,
            #         details={
            #             "declared": "session",
            #             "actual_days": self.calculate_actual_retention_days(actual_cookie.expires)
            #         }
            #     ))

            # Issue 2: Actual expiration exceeds declared by > 30%
            declared_days = self.parse_retention_to_days(policy_cookie.declared_retention)
            actual_days = self.calculate_actual_retention_days(actual_cookie.expires)

            # if declared_days and actual_days and declared_days > 0:
            #     percentage_diff = ((actual_days - declared_days) / declared_days) * 100
            #     if percentage_diff > 30:
            #         issues.append(ComplianceIssue(
            #             issue_id=2,
            #             category="Specific",
            #             type="Retention",
            #             description="Actual expiration exceeds declared duration by more than 30%",
            #             severity="High",
            #             cookie_name=actual_cookie.name,
            #             details={
            #                 "declared_days": declared_days,
            #                 "actual_days": actual_days,
            #                 "percentage_diff": percentage_diff
            #             }
            #         ))
            # Đang thấy thiếu trường hợp: declared_days = None thì xử lý như nào? --> Có thể tách làm một case lớn luôn vì bài toán của mình khác với paper
            # if not declared_days:
            #     issues.append(ComplianceIssue(
            #         issue_id=2,
            #         category="Specific",
            #         type="Retention",
            #         description="Policy has no information about duration.",
            #         severity="High",
            #         cookie_name=actual_cookie.name,
            #         details={
            #             "declared_days": declared_days,
            #             "actual_days": actual_days,
            #             "percentage_diff": 100
            #         }
            #     ))

            # Issue 3: Short-term declared but long-term actual --> OK
            # if (declared_days and declared_days <= 30 and
            #     actual_days and actual_days >= 365):

            #     issues.append(ComplianceIssue(
            #         issue_id=3,
            #         category="Specific",
            #         type="Retention",
            #         description="Policy states short-term retention but observed cookie expires after 1 year",
            #         severity="High",
            #         cookie_name=actual_cookie.name,
            #         details={
            #             "declared_days": declared_days,
            #             "actual_days": actual_days
            #         }
            #     ))

            # Issue 4: Cookie sent to unlisted third party ---> Chưa sử lý thành công.
            # for request_domain in actual_cookie.third_party_requests:
            #     found_in_policy = False
            #     for declared_party in policy_cookie.declared_third_parties:
            #         if declared_party.lower() in request_domain.lower():
            #             found_in_policy = True
            #             break

            #     if not found_in_policy and self.is_third_party_domain(request_domain, main_domain):
            #         issues.append(ComplianceIssue(
            #             issue_id=4,
            #             category="Specific",
            #             type="Third-party",
            #             description="Cookie is sent to a third-party domain not listed in policy",
            #             severity="High",
            #             cookie_name=actual_cookie.name,
            #             details={
            #                 "undeclared_domain": request_domain,
            #                 "declared_parties": policy_cookie.declared_third_parties
            #             }
            #         ))

            # Issue 5: Claims first-party but sent to external tracker --> Chưa xử lý thành công
            # if ("First Party" in policy_cookie.declared_third_parties and
            #     any(self.is_known_ad_tracker(domain) for domain in actual_cookie.third_party_requests)):

            #     issues.append(ComplianceIssue(
            #         issue_id=5,
            #         category="Specific",
            #         type="Third-party",
            #         description="Policy claims first-party only but cookie sent to external tracker",
            #         severity="Critical",
            #         cookie_name=actual_cookie.name,
            #         details={
            #             "tracker_domains": [d for d in actual_cookie.third_party_requests if self.is_known_ad_tracker(d)]
            #         }
            #     ))

            # Issue 6: Declared strictly necessary but used for advertising --> Gặp khó khăn trong viecj suy luận
            # infered_cookie_purpose = self._infer_cookie_purpose(actual_cookie)
            # print("infer: ", actual_cookie.name, infered_cookie_purpose)
            # if (policy_cookie.declared_purpose.lower() == "strictly necessary" and
            #     any(self.is_known_ad_tracker(domain) for domain in actual_cookie.third_party_requests)):

            #     issues.append(ComplianceIssue(
            #         issue_id=6,
            #         category="Specific",
            #         type="Purpose",
            #         description="Cookie declared as 'strictly necessary' but used for advertising",
            #         severity="Critical",
            #         cookie_name=actual_cookie.name,
            #         details={
            #             "declared_purpose": policy_cookie.declared_purpose,
            #             "advertising_domains": [d for d in actual_cookie.third_party_requests if self.is_known_ad_tracker(d)]
            #         }
            #     ))

            # Issue 7: Cookie performs cross-site tracking, session replay, or persistent identification without being described in the policy.

        return issues

    def analyze_general_issues(self, policy_cookies: List[PolicyCookie],
                             actual_cookies: List[ActualCookie],
                             main_domain: str) -> List[ComplianceIssue]:
        """Phân tích các vấn đề general compliance"""
        issues = []
        # Tạo danh sách purpose labels từ policy
        purpose_labels = list(set(cookie.declared_purpose for cookie in policy_cookies))
        purpose_labels_for_checking = ["Strictly Necessary", "Functionality", "Analytical", "Targeting/Advertising/Marketing", "Performance", "Social Sharing"]

        for actual_cookie in actual_cookies:
            # Issue 8: Low semantic similarity with purpose labels --> OK

            max_similarity = 0
            suitable_purpose = None
            for purpose in purpose_labels_for_checking: # purpose_labels:
                similarity = self.calculate_semantic_similarity(actual_cookie.name, purpose)
                if similarity > max_similarity:
                    suitable_purpose = purpose
                    max_similarity = similarity

            # print("Cookie-name: ", actual_cookie.name, "| suitable_purpose: ", suitable_purpose, "| max_similarity: ", max_similarity)
            # if max_similarity < 0.5:
            if suitable_purpose not in purpose_labels:
                issues.append(ComplianceIssue(
                    issue_id=8,
                    category="General",
                    type="Purpose",
                    description="Cookie name shows no semantic similarity with declared purposes",
                    severity="Medium",
                    cookie_name=actual_cookie.name,
                    details={
                        "purpose_similarity": suitable_purpose,
                        "max_similarity": max_similarity,
                        "available_purposes": purpose_labels
                    }
                ))

            # Issue 9: Vague third-party sharing but sent to ad trackers --> Chưa hiểu
            # vague_keywords = ["sharing", "third-party", "partners", "affiliates"]
            # has_vague_third_party = any(
            #     any(keyword in party.lower() for keyword in vague_keywords)
            #     for cookie in policy_cookies
            #     for party in cookie.declared_third_parties
            # )

            # if (has_vague_third_party and
            #     any(self.is_known_ad_tracker(domain) for domain in actual_cookie.third_party_requests)):

            #     issues.append(ComplianceIssue(
            #         issue_id=9,
            #         category="General",
            #         type="Third-party",
            #         description="Vague third-party sharing but cookies sent to advertising trackers",
            #         severity="High",
            #         cookie_name=actual_cookie.name,
            #         details={
            #             "ad_trackers": [d for d in actual_cookie.third_party_requests if self.is_known_ad_tracker(d)]
            #         }
            #     ))

            # Issue 10: "Reasonable time" but exceeds 1 year --> Chưa đạt
            # actual_days = self.calculate_actual_retention_days(actual_cookie.expires)
            # print("Actual days: ", actual_days)

            # reasonable_retention = any(
            #     "reasonable" in cookie.declared_retention.lower()
            #     for cookie in policy_cookies
            # )
            # actual_days = self.calculate_actual_retention_days(actual_cookie.expires)

            # if reasonable_retention and actual_days and actual_days > 365:
            #     issues.append(ComplianceIssue(
            #         issue_id=10,
            #         category="General",
            #         type="Retention",
            #         description="Policy states 'reasonable time' but cookie expires after 1 year",
            #         severity="Medium",
            #         cookie_name=actual_cookie.name,
            #         details={
            #             "actual_days": actual_days
            #         }
            #     ))

        return issues

    def analyze_undefined_issues(self, policy_cookies: List[PolicyCookie],
                               actual_cookies: List[ActualCookie],
                               main_domain: str) -> List[ComplianceIssue]:
        """Phân tích các vấn đề undefined compliance"""
        issues = []

        # Tạo set các cookie names đã được khai báo
        declared_names = {cookie.cookie_name for cookie in policy_cookies}

        for actual_cookie in actual_cookies:
            if actual_cookie.name not in declared_names:
                # Issue 11: No declared purpose but collects data --> chưa chốt hàm infer
                collects_user_data = self._analyzes_cookie_data_collection(actual_cookie)
                transmits_across_domains = len(actual_cookie.third_party_requests) > 0
                persists_across_sessions = (actual_cookie.expires and
                                          self.calculate_actual_retention_days(actual_cookie.expires) > 1)

                if collects_user_data and (transmits_across_domains or persists_across_sessions):
                    inferred_purpose = self._infer_cookie_purpose(actual_cookie)

                    issues.append(ComplianceIssue(
                        issue_id=11,
                        category="Undefined",
                        type="Purpose",
                        description="No declared purpose in policy, yet cookie collects or transmits user data across sessions or domains",
                        severity="High",
                        cookie_name=actual_cookie.name,
                        details={
                            "collects_user_data": collects_user_data,
                            "transmits_across_domains": transmits_across_domains,
                            "persists_across_sessions": persists_across_sessions,
                            "inferred_purpose": inferred_purpose,
                            "data_indicators": self._get_data_collection_indicators(actual_cookie),
                            "cross_domain_requests": actual_cookie.third_party_requests,
                            "retention_days": self.calculate_actual_retention_days(actual_cookie.expires)
                        }
                    ))

                # Issue 12: Silently deployed without consent --> Chưa có căn cứ
                # issues.append(ComplianceIssue(
                #     issue_id=12,
                #     category="Undefined",
                #     type="Behavior",
                #     description="Cookie silently deployed without mention in policy",
                #     severity="Critical",
                #     cookie_name=actual_cookie.name,
                #     details={
                #         "domain": actual_cookie.domain,
                #         "third_party_requests": actual_cookie.third_party_requests
                #     }
                # ))

                # Issue 13: External domain with no third-party info
                if self.is_third_party_domain(actual_cookie.domain, main_domain):
                    issues.append(ComplianceIssue(
                        issue_id=13,
                        category="Undefined",
                        type="Third-party",
                        description="Cookie from external domain with no policy information",
                        severity="High",
                        cookie_name=actual_cookie.name,
                        details={
                            "external_domain": actual_cookie.domain,
                            "main_domain": main_domain
                        }
                    ))

                # Issue 14: Long retention without policy reference
                actual_days = self.calculate_actual_retention_days(actual_cookie.expires)
                if actual_days and actual_days > 365:
                    issues.append(ComplianceIssue(
                        issue_id=14,
                        category="Undefined",
                        type="Retention",
                        description="Cookie persists for extended periods without policy reference",
                        severity="Medium",
                        cookie_name=actual_cookie.name,
                        details={
                            "retention_days": actual_days
                        }
                    ))

        return issues

    def analyze_compliance(self, policy_json: str, actual_cookies: List[ActualCookie],
                          main_domain: str) -> Dict[str, Any]:
        """Phân tích toàn bộ compliance"""
        try:
            policy_cookies = self.parse_policy_data(policy_json)

            specific_issues = self.analyze_specific_issues(policy_cookies, actual_cookies, main_domain)
            general_issues = self.analyze_general_issues(policy_cookies, actual_cookies, main_domain)
            undefined_issues = self.analyze_undefined_issues(policy_cookies, actual_cookies, main_domain)

            all_issues = specific_issues + general_issues + undefined_issues

            # Tính toán thống kê
            severity_counts = {}
            category_counts = {}
            type_counts = {}

            for issue in all_issues:
                severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
                category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
                type_counts[issue.type] = type_counts.get(issue.type, 0) + 1

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
                    for issue in all_issues
                ],
                "statistics": {
                    "by_severity": severity_counts,
                    "by_category": category_counts,
                    "by_type": type_counts
                },
                "policy_cookies_count": len(policy_cookies),
                "actual_cookies_count": len(actual_cookies),
                "compliance_score": max(0, 100 - (len(all_issues) * 5))  # Điểm tuân thủ đơn giản
            }

        except Exception as e:
            print("Error: ", e)
            return {
                "error": str(e),
                "total_issues": 0,
                "issues": [],
                "statistics": {},
                "compliance_score": 0
            }

# Ví dụ sử dụng
def example_usage():
    """Ví dụ sử dụng module"""

    # Dữ liệu policy mẫu
    policy_json = """{
        "is_specific": 1,
        "cookies": [
            {
                "cookie_name": "_ga",
                "declared_purpose": "Analytical",
                "declared_retention": "13 months",
                "declared_third_parties": ["Google Analytics"],
                "declared_description": "This Google Analytics cookie tracks user sessions and behavior."
            },
            {
                "cookie_name": "session_id",
                "declared_purpose": "Strictly Necessary",
                "declared_retention": "Session",
                "declared_third_parties": ["First Party"],
                "declared_description": "Essential cookie for maintaining user login sessions."
            },
            {
                "cookie_name": "check_rule_5",
                "declared_purpose": "Strictly Necessary",
                "declared_retention": "short-term",
                "declared_third_parties": ["First Party"],
                "declared_description": "Essential cookie for maintaining user login sessions."
            }
        ]
    }"""

    # Dữ liệu cookie thực tế mẫu
    actual_cookies = [
        # Dữ liệu kiểm thử
        ActualCookie(
            name="mautic_focus_*",
            value="AKEyXzWkwWgoQyb0usykWs4NlwFLLEwf-h5ba5Tg6y-Rrx6biFAI3LorNWIlR1dcUY1vGWOtKwM",
            domain="example.com",
            expires=datetime.now() + timedelta(days=600),
            secure=True,
            http_only=True,
            same_site="Strict",
            third_party_requests=[]
        ),
        # Dữ liệu chuẩn
        ActualCookie(
            name="_ga",
            value="GA1.2.1234567890.1640995200",
            domain=".example.com",
            expires=datetime.now() + timedelta(days=400),  # Longer than 13 months
            secure=True,
            http_only=False,
            same_site="Lax",
            third_party_requests=["google-analytics.com", "doubleclick.net"]  # Unlisted third party
        ),
        ActualCookie(
            name="session_id",
            value="abc123def456",
            domain="example.com",
            expires=datetime.now() + timedelta(days=2),  # Session but persists 2 days
            secure=True,
            http_only=True,
            same_site="Strict",
            third_party_requests=[]
        ),
        ActualCookie(
            name="pys_fb_pixel_utm_campaign",  # Not in policy
            value="px_user_12345_timestamp_1640995200",
            domain="tracker.com",
            expires=datetime.now() + timedelta(days=730),  # 2 years
            secure=False,
            http_only=False,
            same_site=None,
            third_party_requests=["facebook.com", "twitter.com"]
        )
    ]

    # Phân tích
    analyzer = ViolationAnalyzer()
    result = analyzer.analyze_compliance(policy_json, actual_cookies, "example.com")

    print("=== COOKIE POLICY COMPLIANCE ANALYSIS ===")
    print(f"Total Issues Found: {result['total_issues']}")
    print(f"Compliance Score: {result['compliance_score']}/100")
    print(f"Policy Cookies: {result['policy_cookies_count']}")
    print(f"Actual Cookies: {result['actual_cookies_count']}")

    print("\n=== ISSUES BY SEVERITY ===")
    for severity, count in result['statistics']['by_severity'].items():
        print(f"{severity}: {count}")

    print("\n=== DETAILED ISSUES ===")
    for issue in result['issues']:
        print(f"[{issue['severity']}] Issue #{issue['issue_id']} - {issue['category']}/{issue['type']}")
        print(f"Cookie: {issue['cookie_name']}")
        print(f"Description: {issue['description']}")
        print(f"Details: {issue['details']}")
        print("-" * 50)

if __name__ == "__main__":
    example_usage()
