from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    admin = 'admin'
    cmp_manager = 'cmp_manager'
    provider = 'provider'
    unregistered = 'unregistered'

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class RegisterResponseSchema(BaseModel):
    msg: str

class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = Field(default=UserRole.unregistered)
    requested_role: Optional[UserRole] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    approved_by_admin: bool = Field(default=False)

class UserInfo(BaseModel):
    name: str
    email: EmailStr
    role: UserRole
    approved_by_admin: bool

class LoginResponseSchema(BaseModel):
    token: str
    user: UserInfo

class RequestRoleChangeSchema(BaseModel):
    requested_role: UserRole

class ApproveAccountSchema(BaseModel):
    approved_by_admin: bool
