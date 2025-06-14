from datetime import datetime
from pydantic import Field, HttpUrl
from typing import Optional, List

from src.schemas.base import BaseSchema, PyObjectId
from src.schemas.cookie import PolicyCookieSchema

class WebsiteBase(BaseSchema):
    domain: HttpUrl = Field(..., description="The URL of the website")
    provider_id: Optional[PyObjectId] = Field(default=None)
    last_scanned_at: datetime = Field(default_factory=datetime.now)
    policy_url: Optional[str] = Field(default=None, description="The URL of the cookie policy page")
    detected_language: Optional[str] = Field(default=None)
    original_content: str = Field(...)
    translated_content: Optional[str] = Field(default=None)
    table_content: List[dict] = Field(default_factory=list)
    translated_table_content: Optional[str] = Field(default=None)
    is_specific: int = Field(...)
    cookies: List[PolicyCookieSchema] = Field(default_factory=list)
