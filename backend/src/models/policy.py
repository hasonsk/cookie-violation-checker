from typing import List, Optional
from enum import Enum

from src.models.base import BaseMongoDBModel, PyObjectId

class PolicyContent(BaseMongoDBModel):
    """Data structure for policy content"""
    website_url: str
    policy_url: Optional[str]
    detected_language: Optional[str]
    original_content: str
    translated_content: Optional[str]
    table_content: List[dict]
    translated_table_content: Optional[str]
    error: Optional[str] = None
