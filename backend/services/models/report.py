from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel
from .violation import CookieViolationReport

class WebsiteReport(BaseModel):
    website_url: str
    scan_time: datetime
    policy_found: bool
    policy_url: Optional[str] = None
    total_cookies: int
    violating_cookies: int
    violations_by_type: Dict[str, int]
    violations_by_feature: Dict[str, int]
    cookie_violations: List[CookieViolationReport]
    summary: str
