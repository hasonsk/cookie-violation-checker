from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime

class CookieSubmissionRequest(BaseModel):
    website_url: str
    cookies: List[dict]

class CookieType(str, Enum):
    SPECIFIC = "SPECIFIC"
    GENERAL = "GENERAL"
    UNDEFINED = "UNDEFINED"

class PolicyCookie(BaseModel):
    cookie_name: str
    declared_purpose: Optional[str]
    declared_retention: Optional[str]
    declared_third_parties: List[str]
    declared_description: Optional[str]

class PolicyCookieList(BaseModel):
    is_specific: int
    cookies: List[PolicyCookie]

class ActualCookie(BaseModel):
    name: str
    value: str
    domain: str
    expirationDate: Optional[datetime]
    secure: bool
    httpOnly: bool
    sameSite: Optional[str]
    path: Optional[str] = "/"
