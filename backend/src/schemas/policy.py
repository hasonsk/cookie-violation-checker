from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class PolicyRequest(BaseModel):
    website_url: str

class DiscoveryMethod(str, Enum):
    LINK_TAG = "link_tag"
    FOOTER_LINK = "footer_link"
    NAVIGATION_LINK = "navigation_link"
    BING_SEARCH = "bing_search"
    SITEMAP = "sitemap"

class PolicyContent(BaseModel):
    website_url: str
    policy_url: Optional[str]
    detected_language: Optional[str]
    original_content: str
    translated_content: Optional[str]
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
