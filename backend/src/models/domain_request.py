from enum import Enum
from pydantic import Field
from typing import Optional, List
from datetime import datetime

from src.models.base import BaseMongoDBModel, PyObjectId

class DomainRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DomainRequest(BaseMongoDBModel):
    requester_id: PyObjectId = Field(..., )
    company_name: str = Field(..., description="Name of the company/organization")
    domains: List[str] = Field(default_factory=list, description="List of domains to register")
    purpose: str = Field(..., description="Purpose and reason for domain registration")
    status: DomainRequestStatus = Field(default=DomainRequestStatus.PENDING, description="Current status of the request")
    requester_id: PyObjectId = Field(..., description="ID of the user making the request")
    processed_by: Optional[PyObjectId] = Field(default=None)
    processed_at: Optional[datetime] = Field(default=None)
    feedback: str = Field(default=None, description="Feedback from the admin if the request was rejected")
