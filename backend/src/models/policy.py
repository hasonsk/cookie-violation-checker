from typing import List, Optional
from enum import Enum

from src.models.base import BaseMongoDBModel, PyObjectId

class DiscoveryMethod(str, Enum):
    LINK_TAG = "link_tag"
    FOOTER_LINK = "footer_link"
    NAVIGATION_LINK = "navigation_link"
    BING_SEARCH = "bing_search"
    SITEMAP = "sitemap"

class PolicyContent(BaseMongoDBModel):
    """Data structure for policy content"""
    website_id: PyObjectId
    policy_url: Optional[str]
    # discovery_method: DiscoveryMethod
    detected_language: Optional[str]
    original_content: str
    translated_content: Optional[str]
    table_content: List[dict]
    translated_table_content: Optional[str]
    error: Optional[str] = None
