from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from enum import Enum

class DiscoveryMethod(Enum):
    LINK_TAG = "link_tag"
    FOOTER_LINK = "footer_link"
    NAVIGATION_LINK = "navigation_link"
    BING_SEARCH = "bing_search"
    SITEMAP = "sitemap"

@dataclass
class PolicyDiscoveryResult:
    website_url: str
    policy_url: Optional[str] = None
    discovery_method: Optional[DiscoveryMethod] = None
    error: Optional[str] = None
    confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "website_url": self.website_url,
            "policy_url": self.policy_url,
            "discovery_method": self.discovery_method.value if self.discovery_method else None,
            "error": self.error,
            "confidence_score": self.confidence_score
        }

@dataclass
class PolicyContent:
    """Data structure for policy content"""
    website_url: str
    policy_url: Optional[str]
    original_content: str
    translated_content: Optional[str]
    detected_language: Optional[str]
    table_content: List[dict]
    translated_table_content: Optional[str]
    error: Optional[str] = None

class PolicyExtractResponse(BaseModel):
    """Response schema for policy extraction"""
    website_url: str
    policy_url: Optional[str]
    original_content: str
    translated_content: Optional[str]
    detected_language: Optional[str]
    table_content: List[dict]
    translated_table_content: Optional[str]
    error: Optional[str] = None

class PolicyExtractRequest(BaseModel):
    """Request schema for policy extraction"""
    website_url: str
    policy_url: Optional[str] = None
    translate_to_english: Optional[bool] = True
    force_refresh: Optional[bool] = False
