from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from src.models.base import BaseMongoDBModel, PyObjectId

class CookieType(str, Enum):
    SPECIFIC = "SPECIFIC"
    GENERAL = "GENERAL"
    UNDEFINED = "UNDEFINED"

class PolicyCookie(BaseModel):
    """Cấu trúc cookie được khai báo trong policy"""
    cookie_name: str
    declared_purpose: Optional[str]
    declared_retention: Optional[str]
    declared_third_parties: List[str]
    declared_description: Optional[str]

class PolicyCookieList(BaseModel): # This is not a MongoDB model
    """Cấu trúc danh sách cookie trong policy"""
    is_specific: int
    cookies: List[PolicyCookie]

class ActualCookie(BaseModel): # This is not a MongoDB model
    """Cấu trúc cookie thu thập được thực tế"""
    name: str
    value: str
    domain: str
    expirationDate: Optional[datetime]
    secure: bool
    httpOnly: bool
    sameSite: Optional[str]
    path: Optional[str] = "/"
