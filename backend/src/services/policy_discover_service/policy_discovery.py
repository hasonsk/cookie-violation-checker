from typing import Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum


class DiscoveryMethod(Enum):
    LINK_TAG = "link_tag"
    FOOTER_LINK = "footer_link"
    NAVIGATION_LINK = "navigation_link"
    DIV_LINK = "div_link"
    BING_SEARCH = "bing_search"
    SITEMAP = "sitemap"


class PolicyDiscoveryResult(BaseModel):
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
