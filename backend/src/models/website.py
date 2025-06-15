from datetime import datetime
from pydantic import Field, HttpUrl
from typing import Optional, List
from enum import Enum

from src.models.base import BaseMongoDBModel, PyObjectId
from src.models.cookie import PolicyCookie

class Website(BaseMongoDBModel):
    domain: HttpUrl = Field(..., description="The URL of the website")
    company_name: Optional[str] = Field(default=None, description="The name of the company owning the website") # Add company_name
    provider_id: Optional[PyObjectId] = Field(default=None)
    last_checked_at: datetime = Field(default_factory=datetime.now, description="Date of the most recent check")
    policy_url: Optional[str] = Field(default=None, description="The URL of the cookie policy page")
    detected_language: Optional[str] = Field(default=None)
    original_content: str = Field(...)
    translated_content: Optional[str] = Field(default=None)
    table_content: List[dict] = Field(default_factory=list)
    translated_table_content: Optional[str] = Field(default=None)
    is_specific: int = Field(...)
    policy_cookies: List[PolicyCookie] = Field(default_factory=list)
