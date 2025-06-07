import json
from typing import Dict, List, Any, Callable

# Giữ lại các import cần thiết
from utils.cookie_utils import calculate_actual_retention_days, is_third_party_domain
from schemas.cookie_schema import PolicyCookie, PolicyCookieList, ActualCookie, ComplianceIssue
from .violation_rules import cookie_rules

class ViolationAnalyzer:
    """
    Một "Rule Engine" để phân tích sự tuân thủ cookie bằng cách áp dụng
    một tập hợp các quy tắc có thể mở rộng.
    """
    def __init__(self, rules: List[Callable] = cookie_rules):
        """
        Khởi tạo analyzer với một danh sách các quy tắc.

        Args:
            rules: Danh sách các hàm quy tắc sẽ được áp dụng. Mặc định là cookie_rules.
        """
        self.rules = rules

    def analyze_compliance(
        self,
        policy_cookies: List[PolicyCookie],
        actual_cookies: List[ActualCookie],
        main_domain: str
    ) -> Dict[str, Any]:
        """
        Phân tích sự tuân thủ bằng cách áp dụng tất cả các quy tắc đã đăng ký.
        """
        all_issues = []
        policy_map = {cookie.cookie_name: cookie for cookie in policy_cookies}
        declared_names = set(policy_map.keys())

        for actual_cookie in actual_cookies:
            # Xác định context cho mỗi cookie thực tế
            context = {
                "actual_cookie": actual_cookie,
                "policy_cookie": policy_map.get(actual_cookie.name),
                "policy_cookies": policy_cookies,
                "main_domain": main_domain,
                "is_declared": actual_cookie.name in declared_names,
            }

            for rule_func in self.rules:
                issue = rule_func(context)
                if issue:
                    all_issues.append(issue)

        return self._summarize_results(all_issues, policy_cookies, actual_cookies, main_domain)

    def _summarize_results(
        self,
        all_issues: List[ComplianceIssue],
        policy_cookies: List[PolicyCookie],
        actual_cookies: List[ActualCookie],
        main_domain: str
    ) -> Dict[str, Any]:
        """
        Tổng hợp kết quả phân tích và tính điểm tuân thủ.
        Hàm này giữ nguyên logic tính toán thống kê của bạn.
        """
        severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        category_counts = {"Specific": 0, "General": 0, "Undefined": 0}

        for issue in all_issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1

        severity_weights = {"Critical": 20, "High": 10, "Medium": 5, "Low": 2}
        penalty = sum(severity_weights.get(issue.severity, 5) for issue in all_issues)
        compliance_score = max(0, 100 - penalty)

        return {
            "total_issues": len(all_issues),
            "issues": [issue.dict() for issue in sorted(all_issues, key=lambda x: x.severity)],
            "statistics": {
                "by_severity": severity_counts,
                "by_category": category_counts,
            },
            "policy_cookies_count": len(policy_cookies),
            "actual_cookies_count": len(actual_cookies),
            "compliance_score": compliance_score,
                "summary": {
                    "critical_issues": severity_counts["Critical"],
                    "high_issues": severity_counts["High"],
                    "undeclared_cookies": [c.name for c in actual_cookies
                                             if c.name not in {pc.cookie_name for pc in policy_cookies}],
                    "declared_cookies": [c.cookie_name for c in policy_cookies],
                    "declared_third_parties": [c.declared_third_parties for c in policy_cookies],
                    "third_party_cookies": [c.name for c in actual_cookies
                                              if is_third_party_domain(c.domain, main_domain)],
                    "long_term_cookies": [c.name for c in actual_cookies
                                             if calculate_actual_retention_days(c.expirationDate) and
                                                calculate_actual_retention_days(c.expirationDate) > 365]
                }
        }
