from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, validator


# Enums for standardized values
class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class CookieType(str, Enum):
    """Cookie classification types"""
    SPECIFIC = "specific"
    GENERAL = "general"
    UNDEFINED = "undefined"


class ViolationType(str, Enum):
    """Violation attribute types"""
    RETENTION = "retention"
    THIRD_PARTY = "third_party"
    PURPOSE = "purpose"
    BEHAVIOR = "behavior"


class PolicyStatus(str, Enum):
    """Policy discovery status"""
    FOUND = "found"
    NOT_FOUND = "not_found"
    ACCESS_DENIED = "access_denied"
    TIMEOUT = "timeout"
    ERROR = "error"


# Request Models
class AnalyzeWebsiteRequest(BaseModel):
    """Request to analyze a website for cookie violations"""
    website_url: HttpUrl = Field(..., description="URL of the website to analyze")
    force_refresh: bool = Field(default=False, description="Force refresh analysis")
    include_live_cookies: bool = Field(default=True, description="Include live cookie collection")
    timeout: Optional[int] = Field(default=None, description="Analysis timeout in seconds")

    @validator('website_url')
    def validate_url(cls, v):
        """Validate URL format"""
        url_str = str(v)
        if not url_str.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class LiveCookieData(BaseModel):
    """Live cookie data from Chrome extension"""
    name: str = Field(..., description="Cookie name")
    value: str = Field(..., description="Cookie value")
    domain: str = Field(..., description="Cookie domain")
    path: str = Field(default="/", description="Cookie path")
    expires: Optional[int] = Field(None, description="Expiration timestamp")
    http_only: bool = Field(default=False, description="HttpOnly flag")
    secure: bool = Field(default=False, description="Secure flag")
    same_site: Optional[str] = Field(None, description="SameSite attribute")
    session: bool = Field(default=False, description="Session cookie flag")


class SubmitCookiesRequest(BaseModel):
    """Request to submit live cookies from extension"""
    task_id: str = Field(..., description="Analysis task ID")
    website_url: HttpUrl = Field(..., description="Website URL")
    cookies: List[LiveCookieData] = Field(..., description="List of live cookies")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Collection timestamp")


# Response Models
class TaskResponse(BaseModel):
    """Basic task response"""
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Current task status")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Task creation time")


class PolicyInfo(BaseModel):
    """Cookie policy information"""
    policy_url: Optional[str] = Field(None, description="URL of cookie policy")
    policy_status: PolicyStatus = Field(..., description="Policy discovery status")
    content_length: Optional[int] = Field(None, description="Policy content length")
    last_updated: Optional[datetime] = Field(None, description="Policy last update time")
    language: Optional[str] = Field(None, description="Policy language")


class CookieFeature(BaseModel):
    """Extracted cookie feature"""
    name: str = Field(..., description="Cookie name")
    purpose: Optional[str] = Field(None, description="Cookie purpose")
    retention: Optional[str] = Field(None, description="Retention period")
    third_party: Optional[str] = Field(None, description="Third-party information")
    behavior: Optional[str] = Field(None, description="Cookie behavior")
    cookie_type: CookieType = Field(..., description="Cookie classification")
    confidence_score: float = Field(default=0.0, description="Feature extraction confidence")


class ViolationDetail(BaseModel):
    """Individual violation detail"""
    rule_id: int = Field(..., description="Violation rule ID")
    rule_description: str = Field(..., description="Rule description")
    violation_type: ViolationType = Field(..., description="Type of violation")
    severity: str = Field(..., description="Violation severity level")
    details: str = Field(..., description="Detailed violation explanation")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Supporting evidence")


class CookieViolationReport(BaseModel):
    """Violation report for a single cookie"""
    cookie_name: str = Field(..., description="Cookie name")
    cookie_type: CookieType = Field(..., description="Cookie classification")

    # Policy information
    declared_info: Optional[CookieFeature] = Field(None, description="Declared cookie information")

    # Actual information
    actual_info: LiveCookieData = Field(..., description="Actual cookie data")

    # Violations
    violations: List[ViolationDetail] = Field(default_factory=list, description="List of violations")
    violation_count: int = Field(default=0, description="Total violation count")

    # Status
    policy_match: str = Field(..., description="Policy matching status")
    risk_level: str = Field(default="low", description="Risk level assessment")


class AnalysisReport(BaseModel):
    """Complete analysis report"""
    task_id: str = Field(..., description="Task identifier")
    website_url: str = Field(..., description="Analyzed website URL")

    # Policy information
    policy_info: PolicyInfo = Field(..., description="Policy discovery information")

    # Cookie analysis
    total_cookies_found: int = Field(default=0, description="Total cookies found")
    cookies_with_violations: int = Field(default=0, description="Cookies with violations")
    total_violations: int = Field(default=0, description="Total violations count")

    # Detailed reports
    cookie_reports: List[CookieViolationReport] = Field(
        default_factory=list,
        description="Detailed cookie violation reports"
    )

    # Summary statistics
    violations_by_type: Dict[str, int] = Field(
        default_factory=dict,
        description="Violations grouped by type"
    )
    violations_by_category: Dict[str, int] = Field(
        default_factory=dict,
        description="Violations grouped by category"
    )

    # Analysis metadata
    analysis_duration: float = Field(default=0.0, description="Analysis duration in seconds")
    completed_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis completion time")


class TaskStatusResponse(BaseModel):
    """Task status response"""
    task_id: str = Field(..., description="Task identifier")
    status: TaskStatus = Field(..., description="Current status")
    progress: int = Field(default=0, description="Progress percentage (0-100)")
    message: str = Field(..., description="Current status message")

    # Results (if completed)
    result: Optional[AnalysisReport] = Field(None, description="Analysis results")

    # Error information (if failed)
    error: Optional[str] = Field(None, description="Error message")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Detailed error information")

    # Timing information
    created_at: datetime = Field(..., description="Task creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")


# Health check models
class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: str = Field(..., description="API version")
    dependencies: Dict[str, str] = Field(
        default_factory=dict,
        description="Dependency status"
    )


# Error models
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier")


# Statistics models for dashboard
class ViolationStatistics(BaseModel):
    """Violation statistics"""
    total_analyses: int = Field(default=0, description="Total analyses performed")
    total_violations: int = Field(default=0, description="Total violations found")
    most_violated_rules: List[Dict[str, Union[int, str]]] = Field(
        default_factory=list,
        description="Most frequently violated rules"
    )
    violations_by_domain: Dict[str, int] = Field(
        default_factory=dict,
        description="Violations grouped by domain"
    )
    trend_data: List[Dict[str, Union[str, int]]] = Field(
        default_factory=list,
        description="Violation trends over time"
    )
