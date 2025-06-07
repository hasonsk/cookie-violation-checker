from enum import Enum
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

class CookieType(Enum):
    SPECIFIC = "SPECIFIC"
    GENERAL = "GENERAL"
    UNDEFINED = "UNDEFINED"

class PolicyCookie(BaseModel):
    """Cấu trúc cookie được khai báo trong policy"""
    cookie_name: str
    declared_purpose: Optional[str]
    declared_retention: Optional[str]
    declared_third_parties: List[str]
    declared_description: Optional[str]

class PolicyCookieList(BaseModel):
    """Cấu trúc danh sách cookie trong policy"""
    is_specific: int
    cookies: List[PolicyCookie]

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

class CookieSubmissionRequest(BaseModel):
    website_url: str
    cookies: List[dict]


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
    """Request schema cho compliance analysis"""
    website_url: str
    cookies: List[dict]
    policy_json: Optional[PolicyCookieList] = None


class ComplianceResponse(BaseModel):
    """Response schema cho compliance analysis"""
    total_issues: int
    issues: List[Dict[str, Any]]
    statistics: Dict[str, Any]
    policy_cookies_count: int
    actual_cookies_count: int
    compliance_score: float
    summary: Dict[str, Any]

class ComplianceAnalysisResult(BaseModel):
    """Kết quả phân tích compliance để lưu vào database"""
    website_url: str
    analysis_date: datetime
    total_issues: int
    compliance_score: float
    issues: List[ComplianceIssue]
    statistics: Dict[str, Any]
    summary: Dict[str, Any]
    policy_cookies_count: int
    actual_cookies_count: int

class ComplianceAnalysisResponse(ComplianceAnalysisResult):
    policy_url: Optional[str]
