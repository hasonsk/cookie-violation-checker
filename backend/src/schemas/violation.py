from enum import Enum
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from src.schemas.cookie import PolicyCookieList
from datetime import datetime

class AnalysisPhase(str, Enum):
    DISCOVERY = "policy_discovery"
    EXTRACTION = "content_extraction"
    FEATURE_EXTRACTION = "feature_extraction"
    COMPLIANCE_CHECK = "compliance_check"

class ComplianceIssue(BaseModel):
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
    policy_json: Optional[PolicyCookieList] = None

class ComplianceResponse(BaseModel):
    total_issues: int
    issues: List[ComplianceIssue]
    statistics: Dict[str, Any]
    policy_cookies_count: int
    actual_cookies_count: int
    compliance_score: float
    summary: Dict[str, Any]
    details: Dict[str, Any]

class ComplianceAnalysisResult(BaseModel):
    website_url: str
    analysis_date: datetime
    total_issues: int
    compliance_score: float
    issues: List[ComplianceIssue]
    statistics: Dict[str, Any]
    summary: Dict[str, Any]
    policy_cookies_count: int
    actual_cookies_count: int
    details: Dict[str, Any]

class ComplianceAnalysisResponse(ComplianceAnalysisResult):
    policy_url: Optional[str]
