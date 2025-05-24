from enum import Enum
from typing import Optional
from pydantic import BaseModel

class DiscoveryMethod(Enum):
    LINK_TAG = "link_tag"
    FOOTER_LINK = "footer_link"
    NAVIGATION_LINK = "navigation_link"
    BING_SEARCH = "bing_search"
    SITEMAP = "sitemap"

class PolicyDiscoveryResult(BaseModel):
    website_url: str
    policy_url: Optional[str] = None
    discovery_method: Optional[DiscoveryMethod] = None  # "link_tag", "search_engine", "not_found"
    error: Optional[str] = None
