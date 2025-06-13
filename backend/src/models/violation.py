from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.models.base import BaseMongoDBModel, PyObjectId
from src.models.cookie import PolicyCookie, ActualCookie, PolicyCookieList

class ComplianceIssue(BaseModel): # Not a MongoDB model
    issue_id: int
    category: str
    type: str
    description: str
    severity: str
    cookie_name: str
    details: Dict[str, Any]

class ComplianceSummary(BaseModel):
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    issues_by_category: Dict[str, int]
    undeclared_cookies: List[str]
    declared_cookies: List[str]
    declared_third_parties: List[str]
    third_party_cookies: List[str]
    long_term_cookies: List[str]

class ComplianceAnalysisResult(BaseMongoDBModel):
    website_id: PyObjectId
    feature_id: PyObjectId
    analyzed_at: datetime
    total_issues: int
    compliance_score: float
    issues: List[ComplianceIssue]
    summary:  Dict[str, Any]
    policy_cookies_count: int
    actual_cookies_count: int
    details: Dict[str, Any]
