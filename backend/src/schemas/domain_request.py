from src.models.base import PyObjectId
from pydantic import BaseModel, Field, EmailStr, BeforeValidator
from typing import List, Optional, Annotated
from datetime import datetime
from enum import Enum
from bson import ObjectId
import re

# Regex for basic domain validation (e.g., example.com, sub.example.co.uk)
# This regex allows for subdomains, a domain name, and a top-level domain.
# It does not allow IP addresses or URLs with paths/queries.
DOMAIN_REGEX = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$"

def validate_domain_format(domain: str) -> str:
    if not re.match(DOMAIN_REGEX, domain):
        raise ValueError(f"Invalid domain format: {domain}")
    return domain

DomainString = Annotated[str, BeforeValidator(validate_domain_format)]

class DomainRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DomainRequestCreateSchema(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=200)
    domains: List[DomainString] = Field(..., min_length=1, max_length=100)
    purpose: str = Field(..., min_length=10, max_length=1000)

class DomainRequestResponseSchema(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    requester_id: PyObjectId
    company_name: str
    domains: List[str]
    purpose: str
    status: DomainRequestStatus = DomainRequestStatus.PENDING
    processed_by: Optional[PyObjectId] = None
    processed_at: Optional[datetime] = None
    feedback: str = Field(..., min_length=10, max_length=1000)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat() + "Z",
            ObjectId: str # Re-added for explicit serialization
        }
        # For Pydantic V2, use ConfigDict
        # from pydantic import ConfigDict
        # model_config = ConfigDict(populate_by_name=True, json_encoders={datetime: lambda dt: dt.isoformat() + "Z", ObjectId: str})


class DomainRequestPublic(BaseModel):
    id: str
    domain: str
    status: DomainRequestStatus
    requester_id: str
    feedback: str = Field(..., min_length=10, max_length=1000)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
