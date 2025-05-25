from pydantic import BaseModel
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

class CookieType(Enum):
    """Cookie classification types"""
    SPECIFIC = "specific"
    GENERAL = "general"
    UNDEFINED = "undefined"

class CookiePurpose(Enum):
    """Standard cookie purposes"""
    STRICTLY_NECESSARY = "Strictly Necessary"
    FUNCTIONALITY = "Functionality"
    ANALYTICAL = "Analytical"
    TARGETING = "Targeting/Advertising/Marketing"
    PERFORMANCE = "Performance"
    SOCIAL_SHARING = "Social Sharing"
    UNKNOWN = "Unknown"

@dataclass
class CookieFeature:
    """Individual cookie feature structure"""
    cookie_name: Optional[str]
    declared_purpose: Optional[str]
    declared_retention: Optional[str]
    declared_third_parties: List[str]
    declared_description: Optional[str]
    feature_type: str = CookieType.UNDEFINED.value

@dataclass
class CookieFeatures:
    """Complete cookie features response structure"""
    is_specific: int
    cookies: List[CookieFeature]
class Cookie(BaseModel):
    """Schema cho cookie từ browser extension"""
    name: str
    value: str
    domain: str
    path: str
    secure: bool
    httpOnly: bool
    sameSite: Optional[str] = None
    expirationDate: Optional[datetime] = None

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
    httpOnly: bool
    sameSite: Optional[str]
    thirdParties: Optional[List[str]]

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

class ComplianceResult(BaseModel):
    """Schema cho kết quả phân tích compliance"""
    total_issues: int
    issues: List[ComplianceIssue]
    statistics: Dict[str, Dict[str, int]]
    policy_cookies_count: int
    actual_cookies_count: int
    compliance_score: int


class CookieSubmissionResponse(BaseModel):
    """Schema cho response khi submit cookies"""
    status: str
    count: int
    violation: ComplianceResult
