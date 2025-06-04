from enum import Enum

class AnalysisPhase(Enum):
    DISCOVERY = "policy_discovery"
    EXTRACTION = "content_extraction"
    FEATURE_EXTRACTION = "feature_extraction"
    COMPLIANCE_CHECK = "compliance_check"
