from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel
from enum import Enum
from .cookie import CookieFeatureType

class ViolationType(str, Enum):
    RETENTION = "retention"
    THIRD_PARTY = "third_party"
    PURPOSE = "purpose"
    BEHAVIOR = "behavior"

class Violation(BaseModel):
    cookie_name: str
    rule_id: int
    violation_type: ViolationType
    feature_type: CookieFeatureType
    description: str
    severity: str  # "high", "medium", "low"

class CookieViolationReport(BaseModel):
    cookie_name: str
    domain: str
    value_preview: str
    declared_info: Dict[str, Optional[Union[str, List[str]]]]
    actual_info: Dict[str, Any]
    violations: List[Violation]
    feature_type: CookieFeatureType
