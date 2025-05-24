from typing import Optional, List
from pydantic import BaseModel
from enum import Enum

class CookieFeatureType(str, Enum):
    SPECIFIC = "specific"
    GENERAL = "general"
    UNDEFINED = "undefined"

class CookieFeature(BaseModel):
    name: Optional[str] = None
    purpose: Optional[str] = None
    retention: Optional[str] = None
    third_party: Optional[List[str]] = None
    behavior: Optional[str] = None
    feature_type: CookieFeatureType

class LiveCookie(BaseModel):
    name: str
    domain: str
    path: str
    value: str
    expires: Optional[float] = None
    httpOnly: bool = False
    secure: bool = False
    sameSite: Optional[str] = None
    session: bool = False
