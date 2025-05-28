import json
import re
import base64
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import difflib
from fastapi import FastAPI, HTTPException
import email.utils

class PolicyCookie(BaseModel):
    """Cấu trúc cookie được khai báo trong policy"""
    cookie_name: str
    declared_purpose: str
    declared_retention: str
    declared_third_parties: List[str]
    declared_description: str

class ActualCookie(BaseModel):
    """Cấu trúc cookie thu thập được thực tế"""
    name: str
    value: str
    domain: str
    expirationDate: Optional[datetime]
    secure: bool
    httpOnly: bool
    sameSite: Optional[str]
    path: Optional[str] = "/"

class ComplianceIssue(BaseModel):
    """Cấu trúc vấn đề compliance được phát hiện"""
    issue_id: int
    category: str
    type: str
    description: str
    severity: str
    cookie_name: str
    details: Dict[str, Any]

class ComplianceRequest(BaseModel):
    website_url: str
    cookies: List[dict]
    policy_json: Optional[str] = None  # Cho phép client gửi policy JSON

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

class ViolationAnalyzer:
    """Module phân tích compliance giữa cookie policy và thực tế"""

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

    def parse_policy_data(self, policy_json: str) -> List[PolicyCookie]:
        """Parse dữ liệu policy từ JSON với validation tốt hơn"""
        try:
            if isinstance(policy_json, str):
                data = json.loads(policy_json)
            else:
                data = policy_json

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
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Invalid JSON format: {e}")

    def parse_retention_to_days(self, retention_str: str) -> Optional[int]:
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

    def calculate_actual_retention_days(self, expirationDate: Optional[datetime]) -> Optional[int]:
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

    def analyze_cookie_data_collection(self, cookie: ActualCookie) -> bool:
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
        if self.is_third_party_domain(cookie.domain, main_domain):
            domain_purpose = self.infer_third_party_purpose_from_domain(cookie.domain)
            if domain_purpose != "Unknown Third-party":
                return domain_purpose

        # Analyze based on retention
        retention_days = self.calculate_actual_retention_days(cookie.expirationDate)
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

    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Tính độ tương đồng ngữ nghĩa với xử lý tốt hơn"""
        if not text1 or not text2:
            return 0.0
        return difflib.SequenceMatcher(None, text1.lower().strip(), text2.lower().strip()).ratio()

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
                self.calculate_actual_retention_days(actual_cookie.expirationDate) > 1):

                issues.append(ComplianceIssue(
                    issue_id=1,
                    category="Specific",
                    type="Retention",
                    description="Cookie is declared as 'session' but persists longer than 24 hours",
                    severity="Medium",
                    cookie_name=actual_cookie.name,
                    details={
                        "declared": "session",
                        "actual_days": self.calculate_actual_retention_days(actual_cookie.expirationDate)
                    }
                ))

            # Issue 2: Actual expiration exceeds declared by > 30%
            declared_days = self.parse_retention_to_days(policy_cookie.declared_retention)
            actual_days = self.calculate_actual_retention_days(actual_cookie.expirationDate)

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

            # Issue 2b: Policy không có thông tin về retention
            if not declared_days and actual_days and actual_days > 0:
                issues.append(ComplianceIssue(
                    issue_id=15,
                    category="Specific",
                    type="Retention",
                    description="Policy has no clear retention information while cookie persists",
                    severity="High",
                    cookie_name=actual_cookie.name,
                    details={
                        "declared_retention": policy_cookie.declared_retention,
                        "actual_days": actual_days
                    }
                ))

            # Issue 3: Short-term declared but long-term actual
            if (declared_days and declared_days <= 30 and
                actual_days and actual_days >= 365):

                issues.append(ComplianceIssue(
                    issue_id=3,
                    category="Specific",
                    type="Retention",
                    description="Policy states short-term retention but cookie expires after 1 year",
                    severity="High",
                    cookie_name=actual_cookie.name,
                    details={
                        "declared_days": declared_days,
                        "actual_days": actual_days
                    }
                ))

            # Issue 4: Third-party domain không được khai báo (chỉ dựa trên domain)
            if self.is_third_party_domain(actual_cookie.domain, main_domain):
                cookie_domain_purpose = self.infer_third_party_purpose_from_domain(actual_cookie.domain)

                # Kiểm tra xem domain có được khai báo trong third parties không
                domain_declared = False
                for declared_party in policy_cookie.declared_third_parties:
                    if (declared_party.lower() in actual_cookie.domain.lower() or
                        actual_cookie.domain.lower() in declared_party.lower()):
                        domain_declared = True
                        break

                if not domain_declared and cookie_domain_purpose != "Unknown Third-party":
                    issues.append(ComplianceIssue(
                        issue_id=4,
                        category="Specific",
                        type="Third-party",
                        description="Cookie from third-party domain not declared in policy",
                        severity="High",
                        cookie_name=actual_cookie.name,
                        details={
                            "cookie_domain": actual_cookie.domain,
                            "inferred_purpose": cookie_domain_purpose,
                            "declared_parties": policy_cookie.declared_third_parties
                        }
                    ))

            # Issue 5: First-party claim nhưng domain là third-party
            first_party_claims = ["first party", "first-party", "own", "internal"]
            if any(claim in " ".join(policy_cookie.declared_third_parties).lower()
                   for claim in first_party_claims):
                if self.is_third_party_domain(actual_cookie.domain, main_domain):
                    issues.append(ComplianceIssue(
                        issue_id=5,
                        category="Specific",
                        type="Third-party",
                        description="Policy claims first-party only but cookie is from external domain",
                        severity="Critical",
                        cookie_name=actual_cookie.name,
                        details={
                            "cookie_domain": actual_cookie.domain,
                            "main_domain": main_domain,
                            "declared_parties": policy_cookie.declared_third_parties
                        }
                    ))

            # Issue 6: Strictly necessary nhưng có dấu hiệu tracking
            if policy_cookie.declared_purpose.lower() in ["strictly necessary", "essential", "required"]:
                if (self.is_known_ad_tracker(actual_cookie.domain) or
                    self.analyze_cookie_data_collection(actual_cookie)):

                    inferred_purpose = self.infer_cookie_purpose(actual_cookie, main_domain)
                    if "tracking" in inferred_purpose.lower() or "advertising" in inferred_purpose.lower():
                        issues.append(ComplianceIssue(
                            issue_id=6,
                            category="Specific",
                            type="Purpose",
                            description="Cookie declared as 'strictly necessary' but shows tracking behavior",
                            severity="Critical",
                            cookie_name=actual_cookie.name,
                            details={
                                "declared_purpose": policy_cookie.declared_purpose,
                                "inferred_purpose": inferred_purpose,
                                "collects_data": self.analyze_cookie_data_collection(actual_cookie),
                                "tracker_domain": self.is_known_ad_tracker(actual_cookie.domain)
                            }
                        ))

        return issues

    def analyze_general_issues(self, policy_cookies: List[PolicyCookie],
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
                similarity = self.calculate_semantic_similarity(inferred_purpose, purpose)
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

            # Issue 10: "Reasonable time" nhưng quá 1 năm
            reasonable_retention_cookies = [
                cookie for cookie in policy_cookies
                if "reasonable" in cookie.declared_retention.lower()
            ]

            if reasonable_retention_cookies:
                actual_days = self.calculate_actual_retention_days(actual_cookie.expirationDate)
                if actual_days and actual_days > 365:
                    issues.append(ComplianceIssue(
                        issue_id=10,
                        category="General",
                        type="Retention",
                        description="Policy states 'reasonable time' but cookie expires after 1 year",
                        severity="Medium",
                        cookie_name=actual_cookie.name,
                        details={
                            "actual_days": actual_days,
                            "reasonable_retention_policies": [c.declared_retention for c in reasonable_retention_cookies]
                        }
                    ))

        return issues

    def analyze_undefined_issues(self, policy_cookies: List[PolicyCookie],
                               actual_cookies: List[ActualCookie],
                               main_domain: str) -> List[ComplianceIssue]:
        """Phân tích các vấn đề undefined compliance"""
        issues = []
        declared_names = {cookie.cookie_name for cookie in policy_cookies}

        for actual_cookie in actual_cookies:
            if actual_cookie.name not in declared_names:

                # Issue 11: Cookie thu thập dữ liệu nhưng không có trong policy
                collects_data = self.analyze_cookie_data_collection(actual_cookie)
                is_third_party = self.is_third_party_domain(actual_cookie.domain, main_domain)
                persists_long = (
                    self.calculate_actual_retention_days(actual_cookie.expirationDate) and
                    self.calculate_actual_retention_days(actual_cookie.expirationDate) > 1
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
                            "retention_days": self.calculate_actual_retention_days(actual_cookie.expirationDate)
                        }
                    ))

                # Issue 13: Third-party domain không có thông tin policy
                if is_third_party:
                    issues.append(ComplianceIssue(
                        issue_id=13,
                        category="Undefined",
                        type="Third-party",
                        description="Cookie from external domain with no policy disclosure",
                        severity="High",
                        cookie_name=actual_cookie.name,
                        details={
                            "external_domain": actual_cookie.domain,
                            "main_domain": main_domain,
                            "inferred_purpose": self.infer_third_party_purpose_from_domain(actual_cookie.domain)
                        }
                    ))

                # Issue 14: Retention dài mà không có trong policy
                actual_days = self.calculate_actual_retention_days(actual_cookie.expirationDate)
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
        """Phân tích toàn bộ compliance với error handling tốt hơn"""
        try:
            policy_cookies = self.parse_policy_data(policy_json)

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
                    "undeclared_cookies": [c for c in actual_cookies
                                             if c.name not in {pc.cookie_name for pc in policy_cookies}],
                    "third_party_cookies": [c for c in actual_cookies
                                              if self.is_third_party_domain(c.domain, main_domain)],
                    "long_term_cookies": [c for c in actual_cookies
                                             if self.calculate_actual_retention_days(c.expirationDate) > 365]
                }
            }

        except Exception as e:
            print("Error: ", e)
            return {
                "error": str(e),
            }

app = FastAPI()

@app.post("/analyze_compliance/")
async def analyze_compliance(request: ComplianceRequest):
    try:
        actual_cookies: List[ActualCookie] = [cookie for item in request.cookies if (cookie := parse_cookie(item)) is not None]


        # Load policy JSON (this could be fetched or predefined)
        # For now, using a placeholder policy JSON
        policy_json = json.dumps({
            "cookies": [
                {
                    "cookie_name": "_ga",
                    "declared_purpose": "Analytical",
                    "declared_retention": "13 months",
                    "declared_third_parties": ["Google Analytics"],
                    "declared_description": "Google Analytics tracking cookie."
                },
                {
                    "cookie_name": "session_id",
                    "declared_purpose": "Strictly Necessary",
                    "declared_retention": "Session",
                    "declared_third_parties": ["First Party"],
                    "declared_description": "Session management cookie."
                }
            ]
        })

        # Analyze compliance
        analyzer = ViolationAnalyzer()
        result = analyzer.analyze_compliance(policy_json, actual_cookies, urlparse(request.website_url).netloc)
        print("Compliance Analysis Result:", result)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing compliance: {str(e)}")
