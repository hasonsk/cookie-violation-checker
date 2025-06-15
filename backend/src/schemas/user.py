from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from src.schemas.domain_request import DomainRequestPublic
from src.models.base import PyObjectId # Import PyObjectId from base model

class UserRole(str, Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    PROVIDER = 'provider'

class User(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id") # Use PyObjectId here
    email: str
    password: Optional[str] = None # For creation, not for DB model
    hashed_password: Optional[str] = None # For DB model
    name: str
    role: UserRole
    company_name: Optional[str] = None
    approved_by_admin: bool = False
    domain_requests: Optional[List[DomainRequestPublic]] = None # For public display
    requested_role: Optional[UserRole] = None # Add requested_role to User schema
    requested_at: Optional[str] = None # Add requested_at to User schema
    domains_to_observe: Optional[List[str]] = None # Add domains_to_observe to User schema
    reason: Optional[str] = None # Add reason to User schema
    verification_documents: Optional[List[str]] = None # Add verification_documents to User schema
    admin_notes: Optional[str] = None # Add admin_notes to User schema
    status: Optional[str] = None # Add status to User schema

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str # Encode PyObjectId to string
        }
        from_attributes = True # New in Pydantic v2
