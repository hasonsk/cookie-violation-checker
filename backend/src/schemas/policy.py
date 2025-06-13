from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

# From policy_discovery.py
class PolicyRequest(BaseModel):
    website_url: str

class BulkPolicyRequest(BaseModel):
    website_urls: List[str]

class PolicyDiscoveryResult(BaseModel):
    website_url: str
    policy_url: str
    error: str = None
    confidence_score: float
    discovery_method: str

# From policy_analysis.py
class PolicyAnalysisRequest(BaseModel):
    policy_content: str
    table_content: Optional[str] = None

class DiscoveryMethod(str, Enum):
    LINK_TAG = "link_tag"
    FOOTER_LINK = "footer_link"
    NAVIGATION_LINK = "navigation_link"
    BING_SEARCH = "bing_search"
    SITEMAP = "sitemap"

class PolicyContent(BaseModel):
    website_url: str
    policy_url: Optional[str]
    # discovery_method: DiscoveryMethod
    detected_language: Optional[str]
    original_content: str
    translated_content: Optional[str]
    table_content: List[dict]
    translated_table_content: Optional[str]
    error: Optional[str] = None

# From policy_extraction.py
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
