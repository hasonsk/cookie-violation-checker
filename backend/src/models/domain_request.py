from pyparsing import Enum
from pydantic import Field
from typing import Optional, List
from datetime import datetime

from src.models.base import BaseMongoDBModel, PyObjectId

class RequestStatus(str, Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

class DomainRequest(BaseMongoDBModel):
    requester_id: PyObjectId = Field(..., description="ID of the user making the request")
    domains: List[str] = Field(default_factory=list)
    reason: str
    status: RequestStatus = Field(default=RequestStatus.PENDING)
    processed_at: Optional[datetime] = Field(default=None, description="Time when the request was processed")
    processed_by: Optional[PyObjectId] = Field(default=None, description="ID of the admin processing the request")
    feedback: Optional[str] = None
