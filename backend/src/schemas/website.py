from datetime import datetime
from src.models.base import PyObjectId
from pydantic import BaseModel, Field, HttpUrl, ConfigDict, model_validator
from typing import Optional, List
from src.schemas.cookie import PolicyCookie

class WebsiteBase(BaseModel):
    domain: HttpUrl = Field(..., description="The URL of the website")
    user_id: PyObjectId = Field(..., description="ID of the user who owns this website")
    is_approved: bool = Field(default=False, description="Whether the website has been approved by an admin")
    last_checked_at: datetime = Field(default_factory=datetime.now)
    policy_url: Optional[str] = Field(default=None, description="The URL of the cookie policy page")
    detected_language: Optional[str] = Field(default=None)
    original_content: str = Field(...)
    translated_content: Optional[str] = Field(default=None)
    table_content: List[dict] = Field(default_factory=list)
    translated_table_content: Optional[str] = Field(default=None)
    is_specific: int = Field(...)
    cookies: List[PolicyCookie] = Field(default_factory=list)

class WebsiteCreateSchema(BaseModel):
    domain: HttpUrl = Field(..., description="The URL of the website")
    is_approved: bool = Field(default=False, description="Whether the website has been approved by an admin")
    policy_url: Optional[str] = Field(default=None, description="The URL of the cookie policy page")
    original_content: str = Field(...)
    is_specific: int = Field(...)

    @model_validator(mode='before')
    @classmethod
    def validate_domain_prefix(cls, data: dict):
        if isinstance(data, dict) and 'domain' in data:
            domain = data['domain']
            if isinstance(domain, str) and not (domain.startswith('http://') or domain.startswith('https://')):
                data['domain'] = 'https://' + domain
        return data

class WebsiteUpdateSchema(BaseModel):
    domain: Optional[HttpUrl] = Field(None, description="The URL of the website")
    policy_url: Optional[str] = Field(None, description="The URL of the cookie policy page")
    original_content: Optional[str] = Field(None)
    translated_content: Optional[str] = Field(None)
    table_content: Optional[List[dict]] = Field(None)
    translated_table_content: Optional[str] = Field(None)
    is_specific: Optional[int] = Field(None)
    cookies: Optional[List[PolicyCookie]] = Field(None)

class WebsiteResponseSchema(WebsiteBase):
    model_config = ConfigDict(
        populate_by_name=True,  # Allow both alias and field name
        arbitrary_types_allowed=True,
        from_attributes=True,
        str_strip_whitespace=True
    )
    id: PyObjectId = Field(alias="_id")

class WebsiteListResponseSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,  # Allow both alias and field name
        arbitrary_types_allowed=True,
        from_attributes=True,
        str_strip_whitespace=True
    )

    id: PyObjectId = Field(alias="_id")
    domain: str = Field(..., description="The domain name of the website")
    policy_status: str = Field(default="unknown", description="Status of the cookie policy")
    policy_url: Optional[str] = Field(default=None, description="URL of the cookie policy page")
    last_checked_at: Optional[datetime] = Field(default=None, description="Date of the most recent check")
    num_specified_cookies: int = Field(default=0, description="Number of cookies specified in the policy")

class PaginatedWebsiteResponseSchema(BaseModel):
    websites: List[WebsiteListResponseSchema]
    total_count: int
    page: int
    page_size: int
