from pydantic import Field, EmailStr
from typing import Optional
from enum import Enum

from src.models.base import BaseMongoDBModel

class UserRole(str, Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    PROVIDER = 'provider'

class User(BaseMongoDBModel):
    name: str
    email: EmailStr
    password: str
    company_name: Optional[str] = None
    role: UserRole = Field(default=UserRole.PROVIDER)
    approved_by_admin: bool = Field(default=False)
