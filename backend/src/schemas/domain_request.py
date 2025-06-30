from src.models.base import PyObjectId
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum
from bson import ObjectId
from src.schemas.user import UserPublicSchema # Import UserPublicSchema
from src.utils.validation_utils import DomainString # Import DomainString

class DomainRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DomainRequestCreateSchema(BaseModel):
    domains: List[DomainString] = Field(..., min_length=1, max_length=100)
    purpose: str = Field(..., min_length=10, max_length=1000)
    status: DomainRequestStatus = DomainRequestStatus.PENDING # Default status to PENDING

class DomainRequestResponseSchema(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    requester_id: PyObjectId
    requester_username: str
    requester_email: str
    domains: List[str]
    purpose: str
    status: DomainRequestStatus = DomainRequestStatus.PENDING
    processed_by: Optional[PyObjectId] = None
    processed_by_info: Optional[UserPublicSchema] = None
    processed_at: Optional[datetime] = None
    feedback: Optional[str] = Field(None, min_length=10, max_length=1000)
    requester_info: Optional[UserPublicSchema] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        # Pydantic v2 handles datetime and ObjectId serialization automatically
        # json_encoders = {
        #     datetime: lambda dt: dt.isoformat() + "Z",
        #     ObjectId: str
        # }

class DomainRequestPublic(BaseModel):
    id: str
    domain: str
    status: DomainRequestStatus
    requester_id: str
    feedback: str = Field(..., min_length=10, max_length=1000)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class DomainRequestUpdateSchema(BaseModel):
    status: Optional[DomainRequestStatus] = None
    processed_by: Optional[PyObjectId] = None
    processed_at: Optional[datetime] = None
    feedback: Optional[str] = Field(None, min_length=10, max_length=1000)
