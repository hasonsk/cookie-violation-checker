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
    id: Optional[PyObjectId] = Field(None, alias="_id")
    email: str
    password: Optional[str] = None
    name: str
    role: UserRole
    status: Optional[str] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str # Encode PyObjectId to string
        }
        from_attributes = True # New in Pydantic v2
