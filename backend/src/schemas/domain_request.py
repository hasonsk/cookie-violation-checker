from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum
from src.models.base import PyObjectId # Import PyObjectId

class DomainRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DomainRequestCreateSchema(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=200)
    domains: List[str] = Field(..., min_items=1, max_items=100)
    purpose: str = Field(..., min_length=10, max_length=1000)

class DomainRequestResponseSchema(BaseModel):
    id: PyObjectId = Field(..., alias="_id") # Use PyObjectId
    user_id: PyObjectId # Use PyObjectId
    company_name: str
    domains: List[str]
    purpose: str
    status: DomainRequestStatus = DomainRequestStatus.PENDING
    created_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat() + "Z",
    PyObjectId: str # Re-added for explicit serialization
}

class DomainRequestPublic(BaseModel):
    id: str
    domain: str
    status: DomainRequestStatus
    user_id: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
