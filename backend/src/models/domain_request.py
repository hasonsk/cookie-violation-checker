from enum import Enum
from pydantic import Field
from typing import Optional, List
from datetime import datetime, timezone

from src.models.base import BaseMongoDBModel, PyObjectId

class DomainRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DomainRequest(BaseMongoDBModel):
    requester_id: PyObjectId = Field(..., description="ID of the user making the request")
    requester_username: str = Field(..., description="Username of the user making the request")
    requester_email: str = Field(..., description="Email of the user making the request")
    domains: List[str] = Field(default_factory=list, description="List of domains to register")
    purpose: str = Field(..., description="Purpose and reason for domain registration")
    status: DomainRequestStatus = Field(default=DomainRequestStatus.PENDING, description="Current status of the request")
    processed_by: Optional[PyObjectId] = Field(default=None)
    processed_at: Optional[datetime] = Field(default=None)
    feedback: Optional[str] = Field(default=None, description="Feedback from the admin if the request was rejected")
