"""
Module này chứa tất cả các quy tắc kiểm tra vi phạm cookie.
Mỗi quy tắc là một hàm độc lập, nhận một `context` và trả về một `ComplianceIssue` nếu có vi phạm,
hoặc `None` nếu không.
"""
from typing import Optional, Dict, Any, List

from src.schemas.cookie import PolicyCookie, ActualCookie
from src.schemas.violation import ComplianceIssue
from src.utils.cookie_utils import (
    calculate_actual_retention_days,
    parse_retention_to_days,
    is_third_party_domain,
    calculate_semantic_similarity,
    analyze_cookie_data_collection
)
from src.configs.settings import settings

# ================= HELPER FUNCTION =================

def create_issue(
    issue_id: int,
    category: str,
    violation_type: str,
    description: str,
    severity: str,
    cookie: ActualCookie,
    details: Dict[str, Any]
) -> ComplianceIssue:
    """Hàm Factory để tạo một đối tượng ComplianceIssue, giúp giảm lặp code."""
    return ComplianceIssue(
        issue_id=issue_id,
        category=category,
        type=violation_type,
        description=description,
        severity=severity,
        cookie_name=cookie.name,
        details=details
    )

# ================= SPECIFIC VIOLATION RULES =================

def check_rule_1_session_retention(context: Dict[str, Any]) -> Optional[ComplianceIssue]:
    """Quy tắc 1: Cookie khai báo là 'session' nhưng tồn tại lâu hơn 24 giờ."""
    if not context["is_declared"]: return None
    policy: PolicyCookie = context["policy_cookie"]
    actual: ActualCookie = context["actual_cookie"]

    if policy.declared_retention and policy.declared_retention.lower() == 'session':
        actual_hours = calculate_actual_retention_days(actual.expirationDate) * 24
        if actual_hours > settings.violation.SESSION_THRESHOLD_HOURS:
            return create_issue(
                issue_id=1, category="Specific", violation_type="Retention",
                description=f"Cookie is declared as 'session' but persists longer than {settings.violation.SESSION_THRESHOLD_HOURS} hours.",
                severity="Medium", cookie=actual,
                details={"declared": "session", "actual_hours": round(actual_hours)}
            )
    return None

def check_rule_2_retention_mismatch(context: Dict[str, Any]) -> Optional[ComplianceIssue]:
    """Quy tắc 2: Thời gian sống thực tế vượt quá khai báo > 30%."""
    if not context["is_declared"]: return None
    policy: PolicyCookie = context["policy_cookie"]
    actual: ActualCookie = context["actual_cookie"]

    declared_days = parse_retention_to_days(policy.declared_retention)
    actual_days = calculate_actual_retention_days(actual.expirationDate)

    if declared_days and actual_days and declared_days > 0:
        diff = actual_days - declared_days
        if diff > 0:
            percentage_diff = (diff / declared_days) * 100
            if percentage_diff > settings.violation.RETENTION_THRESHOLD_PERCENTAGE:
                return create_issue(
                    issue_id=2, category="Specific", violation_type="Retention",
                    description=f"Actual expiration exceeds declared duration by more than {settings.violation.RETENTION_THRESHOLD_PERCENTAGE}%.",
                    severity="High", cookie=actual,
                    details={
                        "declared_days": declared_days, "actual_days": actual_days,
                        "percentage_diff": round(percentage_diff, 2)
                    }
                )
    return None

def check_rule_3_short_term_vs_long_term(context: Dict[str, Any]) -> Optional[ComplianceIssue]:
    """Quy tắc 3: Chính sách ghi ngắn hạn (<1 năm) nhưng cookie tồn tại > 1 năm."""
    if not context["is_declared"]: return None
    policy: PolicyCookie = context["policy_cookie"]
    actual: ActualCookie = context["actual_cookie"]

    declared_days = parse_retention_to_days(policy.declared_retention)
    actual_days = calculate_actual_retention_days(actual.expirationDate)

    if declared_days and actual_days and declared_days < settings.violation.LONG_TERM_RETENTION_DAYS:
        if actual_days > settings.violation.LONG_TERM_RETENTION_DAYS:
            return create_issue(
                issue_id=3, category="Specific", violation_type="Retention",
                description=f"Policy states short-term retention ({declared_days} days), but cookie persists for over a year.",
                severity="High", cookie=actual,
                details={"declared_days": declared_days, "actual_days": actual_days}
            )
    return None

def check_rule_4_undeclared_third_party(context: Dict[str, Any]) -> Optional[ComplianceIssue]:
    """Quy tắc 4: Cookie gửi đến bên thứ ba không được liệt kê trong chính sách."""
    if not context["is_declared"]: return None
    policy: PolicyCookie = context["policy_cookie"]
    actual: ActualCookie = context["actual_cookie"]
    main_domain: str = context["main_domain"]

    if is_third_party_domain(actual.domain, main_domain):
        declared_parties = [party.lower() for party in policy.declared_third_parties]
        actual_domain_lower = actual.domain.lower()

        # Check if actual domain is a subdomain of any declared party
        is_declared = any(actual_domain_lower.endswith(party) for party in declared_parties)

        if not is_declared:
            return create_issue(
                issue_id=4, category="Specific", violation_type="Third-party",
                description="Cookie is sent to a third-party domain not listed in the policy.",
                severity="High", cookie=actual,
                details={"undeclared_domain": actual.domain, "declared_parties": policy.declared_third_parties}
            )
    return None

def check_rule_5_claimed_first_party_is_third_party(context: Dict[str, Any]) -> Optional[ComplianceIssue]:
    """Quy tắc 5: Chính sách ghi là first-party nhưng cookie gửi đến tracker bên ngoài."""
    if not context["is_declared"]: return None
    policy: PolicyCookie = context["policy_cookie"]
    actual: ActualCookie = context["actual_cookie"]

    declared_parties = [p.lower() for p in policy.declared_third_parties]
    is_claimed_first_party = any(p in ["first party", "no", "none"] for p in declared_parties)

    is_known_tracker = any(tracker in actual.domain.lower() for tracker in settings.violation.KNOWN_AD_TRACKERS)

    if is_claimed_first_party and is_known_tracker:
        return create_issue(
            issue_id=5, category="Specific", violation_type="Third-party",
            description="Policy claims first-party only, but cookie is sent to a known external tracker.",
            severity="Critical", cookie=actual,
            details={"claimed": policy.declared_third_parties, "actual_tracker_domain": actual.domain}
        )
    return None

def check_rule_6_necessary_cookie_is_tracking(context: Dict[str, Any]) -> Optional[ComplianceIssue]:
    """Quy tắc 6: Khai báo là 'strictly necessary' nhưng lại dùng để quảng cáo/theo dõi."""
    if not context["is_declared"]: return None
    policy: PolicyCookie = context["policy_cookie"]
    actual: ActualCookie = context["actual_cookie"]

    if policy.declared_purpose and policy.declared_purpose.lower() == 'strictly necessary':
        is_tracking_cookie = any(tracker in actual.name.lower() for tracker in ['track', 'ad', 'analytics', '_ga']) or \
                               any(tracker in actual.domain.lower() for tracker in settings.violation.KNOWN_AD_TRACKERS)

        if is_tracking_cookie:
            return create_issue(
                issue_id=6, category="Specific", violation_type="Purpose",
                description="Cookie is declared as 'strictly necessary' but appears to be used for tracking or advertising.",
                severity="Critical", cookie=actual,
                details={"declared_purpose": "Strictly Necessary", "inferred_behavior": "Tracking/Advertising"}
            )
    return None

def check_rule_7_unreported_behavior(context: Dict[str, Any]) -> Optional[ComplianceIssue]:
    """Quy tắc 7: Cookie có hành vi theo dõi chéo trang không được mô tả."""
    # Logic này chỉ có thể suy luận. Phân tích traffic thực tế sẽ chính xác hơn.
    if not context["is_declared"]: return None
    policy: PolicyCookie = context["policy_cookie"]
    actual: ActualCookie = context["actual_cookie"]

    is_cross_site_tracker = is_third_party_domain(actual.domain, context["main_domain"]) and \
                           any(tracker in actual.domain.lower() for tracker in settings.violation.KNOWN_AD_TRACKERS)

    description = policy.declared_description.lower() if policy.declared_description else ""
    behavior_is_described = any(term in description for term in ["track", "ad", "target", "profile"])

    if is_cross_site_tracker and not behavior_is_described:
        return create_issue(
            issue_id=7, category="Specific", violation_type="Behavior",
            description="Cookie performs cross-site tracking, but this behavior is not described in the policy.",
            severity="Critical", cookie=actual,
            details={"behavior": "Cross-site tracking", "policy_description": policy.declared_description}
        )
    return None

# ================= GENERAL VIOLATION RULES =================

def check_rule_8_low_semantic_similarity(context: Dict[str, Any]) -> Optional[ComplianceIssue]:
    """Quy tắc 8: Tên cookie không tương đồng ngữ nghĩa với bất kỳ mục đích nào được khai báo."""
    if not context["is_declared"]: return None # Chỉ áp dụng cho cookie được khai báo chung
    policy_cookies: List[PolicyCookie] = context["policy_cookies"]
    actual: ActualCookie = context["actual_cookie"]

    declared_purposes = list(set([p.declared_purpose for p in policy_cookies if p.declared_purpose] + settings.violation.STANDARD_PURPOSE_LABELS))
    if not declared_purposes: return None

    similarities = [calculate_semantic_similarity(actual.name, purpose) for purpose in declared_purposes]
    max_similarity = max(similarities) if similarities else 0

    if max_similarity < settings.violation.SEMANTIC_SIMILARITY_THRESHOLD:
        return create_issue(
            issue_id=8, category="General", violation_type="Purpose",
            description=f"Observed cookie name shows no semantic similarity with any declared purpose label (max similarity < {settings.violation.SEMANTIC_SIMILARITY_THRESHOLD}).",
            severity="Medium", cookie=actual,
            details={"cookie_name": actual.name, "max_similarity": round(max_similarity, 2), "declared_purposes": declared_purposes}
        )
    return None

def check_rule_9_vague_third_party_sharing(context: Dict[str, Any]) -> Optional[ComplianceIssue]:
    """Quy tắc 9: Chính sách mơ hồ về 'chia sẻ' nhưng cookie gửi đến tracker quảng cáo."""
    actual: ActualCookie = context["actual_cookie"]
    is_known_tracker = any(tracker in actual.domain.lower() for tracker in settings.violation.KNOWN_AD_TRACKERS)

    if is_known_tracker:
        policy_cookies: List[PolicyCookie] = context["policy_cookies"]
        # Tìm xem có chính sách nào nói chung chung về "third-party" không
        has_vague_policy = any(
            "third-part" in (p.declared_description.lower() if p.declared_description else "")
            for p in policy_cookies if not p.cookie_name # Áp dụng cho mục đích chung
        )
        if has_vague_policy:
            return create_issue(
                issue_id=9, category="General", violation_type="Third-party",
                description="Policy vaguely mentions third-party sharing, but cookie is sent to a known advertising tracker without specific disclosure.",
                severity="High", cookie=actual,
                details={"tracker_domain": actual.domain}
            )
    return None

def check_rule_10_vague_retention(context: Dict[str, Any]) -> Optional[ComplianceIssue]:
    """Quy tắc 10: Chính sách nói 'thời gian hợp lý' nhưng cookie tồn tại > 1 năm."""
    actual: ActualCookie = context["actual_cookie"]
    actual_days = calculate_actual_retention_days(actual.expirationDate)

    if actual_days > settings.violation.LONG_TERM_RETENTION_DAYS:
        policy_cookies: List[PolicyCookie] = context["policy_cookies"]
        # Tìm xem có chính sách nào nói chung chung về retention không
        has_vague_retention = any(
            any(term in (p.declared_description.lower() if p.declared_description else "") for term in ["reasonable", "necessary period"])
            for p in policy_cookies if not p.cookie_name
        )
        if has_vague_retention:
             return create_issue(
                issue_id=10, category="General", violation_type="Retention",
                description="Policy states a vague retention period (e.g., 'reasonable time'), but cookie persists for over a year.",
                severity="Medium", cookie=actual,
                details={"actual_days": actual_days}
            )
    return None

# ================= UNDEFINED VIOLATION RULES =================

def check_rule_11_undeclared_purpose(context: Dict[str, Any]) -> Optional[ComplianceIssue]:
    """Quy tắc 11: Cookie không được khai báo nhưng thu thập dữ liệu người dùng."""
    if context["is_declared"]: return None

    actual: ActualCookie = context["actual_cookie"]
    collects_data = analyze_cookie_data_collection(actual)

    if collects_data:
        return create_issue(
            issue_id=11, category="Undefined", violation_type="Purpose",
            description="Cookie is not declared in the policy, yet it appears to collect or transmit user data.",
            severity="High", cookie=actual,
            details={"collects_user_data": True, "value_snippet": actual.value[:50] + "..."}
        )
    return None

def check_rule_12_silent_deployment(context: Dict[str, Any]) -> Optional[ComplianceIssue]:
    """Quy tắc 12: Cookie được triển khai âm thầm (Không thể kiểm tra hoàn toàn ở backend)."""
    # Ghi chú: Quy tắc này liên quan đến sự đồng ý (consent), khó xác định ở backend.
    # Chúng ta có thể đánh dấu nó như một rủi ro tiềm tàng nếu cookie không được khai báo.
    if context["is_declared"]: return None

    return create_issue(
        issue_id=12, category="Undefined", violation_type="Behavior",
        description="Cookie is deployed without being mentioned in the policy, potentially without user consent.",
        severity="Medium", cookie=context["actual_cookie"],
        details={"note": "This check is based on the absence of the cookie in the policy. Verifying user consent requires client-side analysis."}
    )

def check_rule_13_undeclared_third_party_involvement(context: Dict[str, Any]) -> Optional[ComplianceIssue]:
    """Quy tắc 13: Cookie thuộc bên thứ ba nhưng chính sách không đề cập đến bên thứ ba."""
    if context["is_declared"]: return None
    actual: ActualCookie = context["actual_cookie"]
    main_domain: str = context["main_domain"]

    if is_third_party_domain(actual.domain, main_domain):
        policy_cookies: List[PolicyCookie] = context["policy_cookies"]
        # Kiểm tra toàn bộ chính sách xem có đề cập đến bên thứ 3 không
        mentions_third_party = any(
            p.declared_third_parties for p in policy_cookies
        )
        if not mentions_third_party:
            return create_issue(
                issue_id=13, category="Undefined", violation_type="Third-party",
                description="An undeclared cookie belongs to an external domain, but the policy contains no information about third-party involvement.",
                severity="High", cookie=actual,
                details={"third_party_domain": actual.domain}
            )
    return None

def check_rule_14_undeclared_long_term_retention(context: Dict[str, Any]) -> Optional[ComplianceIssue]:
    """Quy tắc 14: Chính sách không nói về thời gian lưu trữ nhưng cookie tồn tại rất lâu."""
    if context["is_declared"]: return None
    actual: ActualCookie = context["actual_cookie"]
    actual_days = calculate_actual_retention_days(actual.expirationDate)

    if actual_days > settings.violation.LONG_TERM_RETENTION_DAYS:
        policy_cookies: List[PolicyCookie] = context["policy_cookies"]
        # Kiểm tra toàn bộ chính sách xem có nói về retention không
        mentions_retention = any(p.declared_retention for p in policy_cookies)
        if not mentions_retention:
            return create_issue(
                issue_id=14, category="Undefined", violation_type="Retention",
                description="Policy omits any reference to retention, but this undeclared cookie persists for over a year.",
                severity="Medium", cookie=actual,
                details={"actual_days": actual_days}
            )
    return None

# ================= REGISTER ALL RULES =================
# Danh sách tất cả các quy tắc sẽ được áp dụng.
# Thêm, bớt, hoặc sắp xếp lại các quy tắc ở đây một cách dễ dàng.
cookie_rules = [
    # Specific Rules
    check_rule_1_session_retention,
    check_rule_2_retention_mismatch,
    check_rule_3_short_term_vs_long_term,
    check_rule_4_undeclared_third_party,
    check_rule_5_claimed_first_party_is_third_party,
    check_rule_6_necessary_cookie_is_tracking,
    check_rule_7_unreported_behavior,
    # General Rules
    check_rule_8_low_semantic_similarity,
    check_rule_9_vague_third_party_sharing,
    check_rule_10_vague_retention,
    # Undefined Rules
    check_rule_11_undeclared_purpose,
    check_rule_12_silent_deployment,
    check_rule_13_undeclared_third_party_involvement,
    check_rule_14_undeclared_long_term_retention,
]
