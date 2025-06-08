from typing import Dict, List, Any, Callable
from collections import Counter
from loguru import logger

from src.utils.cookie_utils import calculate_actual_retention_days, is_third_party_domain, parse_retention_to_days
from src.schemas.cookie_schema import PolicyCookie, ActualCookie, ComplianceIssue
from src.services.violation_detect_service.violation_rules import cookie_rules

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
        all_issues = []
        policy_map = {cookie.cookie_name: cookie for cookie in policy_cookies}
        declared_names = set(policy_map.keys())

        for actual_cookie in actual_cookies:
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

        return self._generate_compliance_report(all_issues, policy_cookies, actual_cookies, main_domain)

    def _generate_compliance_report(
        self,
        all_issues: List[ComplianceIssue],
        policy_cookies: List[PolicyCookie],
        actual_cookies: List[ActualCookie],
        main_domain: str
    ) -> Dict[str, Any]:
        severity_counts = _count_by_severity(all_issues)
        category_counts = _count_by_category(all_issues)
        compliance_score = _calculate_compliance_score(all_issues)

        policy_map = {cookie.cookie_name: cookie for cookie in policy_cookies}
        declared_names = set(policy_map.keys())

        undeclared_actual_cookies = [c for c in actual_cookies if c.name not in declared_names]
        declared_policy_cookies = [pc for pc in policy_cookies]
        third_party_actual_cookies = [c for c in actual_cookies if is_third_party_domain(c.domain, main_domain)]
        long_term_actual_cookies = [c for c in actual_cookies if calculate_actual_retention_days(c.expirationDate) and calculate_actual_retention_days(c.expirationDate) > 365]

        declared_violating_cookies = _detect_declared_violations(policy_cookies, actual_cookies, all_issues)
        declared_compliant_cookies = _detect_compliant_cookies(policy_cookies, actual_cookies, all_issues)
        declared_by_third_party_stats = _group_declared_by_third_party(declared_policy_cookies)
        retention_violations = _detect_retention_violations(policy_cookies, actual_cookies)

        result =  {
            "total_issues": len(all_issues),
            "issues": [i.dict() for i in sorted(all_issues, key=lambda x: x.severity)],
            "statistics": {
                "by_severity": severity_counts,
                "by_category": category_counts,
            },
            "policy_cookies_count": len(policy_cookies),
            "actual_cookies_count": len(actual_cookies),
            "compliance_score": compliance_score,
            "summary": {
                "critical_issues": severity_counts.get("Critical", 0),
                "high_issues": severity_counts.get("High", 0),
                "undeclared_cookies": [c.name for c in undeclared_actual_cookies],
                "declared_cookies": [pc.cookie_name for pc in declared_policy_cookies],
                "declared_third_parties": list(set(tp for pc in declared_policy_cookies for tp in pc.declared_third_parties if tp)),
                "third_party_cookies": [c.name for c in third_party_actual_cookies],
                "long_term_cookies": [c.name for c in long_term_actual_cookies],
            },
            "details": {
                "declared_cookie_details": [pc.dict() for pc in declared_policy_cookies],
                "undeclared_cookie_details": [c.dict() for c in undeclared_actual_cookies],
                "declared_violating_cookies": [c.dict() for c in declared_violating_cookies],
                "declared_compliant_cookies": [pc.dict() for pc in declared_compliant_cookies],
                "third_party_domains": {
                    "actual": list({c.domain for c in third_party_actual_cookies}),
                    "declared": list({tp for pc in declared_policy_cookies for tp in pc.declared_third_parties if tp})
                },
                "declared_by_third_party": declared_by_third_party_stats,
                "expired_cookies_vs_declared": retention_violations,
            }
        }
        return result

# Helper functions (outside the class)
def _count_by_severity(all_issues: List[ComplianceIssue]) -> Dict[str, int]:
    severity_counts = Counter(issue.severity for issue in all_issues)
    return {s: severity_counts.get(s, 0) for s in ["Critical", "High", "Medium", "Low"]}

def _count_by_category(all_issues: List[ComplianceIssue]) -> Dict[str, int]:
    category_counts = Counter(issue.category for issue in all_issues)
    return {c: category_counts.get(c, 0) for c in ["Specific", "General", "Undefined"]}

def _calculate_compliance_score(all_issues: List[ComplianceIssue]) -> int:
    severity_weights = {"Critical": 20, "High": 10, "Medium": 5, "Low": 2}
    penalty = sum(severity_weights.get(issue.severity, 5) for issue in all_issues)
    return max(0, 100 - penalty)

def _detect_declared_violations(policy_cookies: List[PolicyCookie], actual_cookies: List[ActualCookie], all_issues: List[ComplianceIssue]) -> List[ActualCookie]:
    violating_cookie_names = {issue.cookie_name for issue in all_issues if issue.cookie_name in {pc.cookie_name for pc in policy_cookies}}
    return [c for c in actual_cookies if c.name in violating_cookie_names]

def _detect_compliant_cookies(policy_cookies: List[PolicyCookie], actual_cookies: List[ActualCookie], all_issues: List[ComplianceIssue]) -> List[PolicyCookie]:
    declared_cookie_names = {pc.cookie_name for pc in policy_cookies}
    violating_cookie_names = {issue.cookie_name for issue in all_issues}
    compliant_names = declared_cookie_names - violating_cookie_names
    return [pc for pc in policy_cookies if pc.cookie_name in compliant_names]

def _group_declared_by_third_party(declared_policy_cookies: List[PolicyCookie]) -> Dict[str, List[Dict[str, Any]]]:
    grouped = {}
    for pc in declared_policy_cookies:
        for tp in pc.declared_third_parties:
            if tp not in grouped:
                grouped[tp] = []
            grouped[tp].append(pc.dict())
    return grouped

def _detect_retention_violations(policy_cookies: List[PolicyCookie], actual_cookies: List[ActualCookie]) -> List[Dict[str, Any]]:
    violations = []
    policy_map = {pc.cookie_name: pc for pc in policy_cookies}
    for actual_cookie in actual_cookies:
        if actual_cookie.name in policy_map:
            policy_cookie = policy_map[actual_cookie.name]
            actual_retention_days = calculate_actual_retention_days(actual_cookie.expirationDate)
            declared_retention_days = parse_retention_to_days(policy_cookie.declared_retention)

            # Only compare if both are numerical and declared retention is not 'session'/'persistent' etc.
            if declared_retention_days is not None and actual_retention_days is not None and actual_retention_days > declared_retention_days:
                violations.append({
                    "cookie_name": actual_cookie.name,
                    "actual_retention_days": actual_retention_days,
                    "declared_retention_string": policy_cookie.declared_retention,
                    "declared_retention_days": declared_retention_days,
                    "issue_description": f"Actual retention ({actual_retention_days} days) exceeds declared retention ({declared_retention_days} days based on '{policy_cookie.declared_retention}')."
                })
    return violations
