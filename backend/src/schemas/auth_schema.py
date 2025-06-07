from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from bson import ObjectId
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
    id: Optional[str] = Field(alias="_id", default=None)
    name: str
    email: EmailStr
    password: str
    role: UserRole = Field(default=UserRole.unregistered)
    requested_role: Optional[UserRole] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    approved_by_admin: bool = Field(default=False)

class UserInfo(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    name: str
    email: EmailStr
    role: UserRole
    approved_by_admin: bool

    @validator("id", pre=True, always=True)
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

class LoginResponseSchema(BaseModel):
    token: str
    user: UserInfo

class RequestRoleChangeSchema(BaseModel):
    requested_role: UserRole

class RequestRoleChangePayloadSchema(BaseModel):
    requested_role: UserRole
    domains_to_observe: Optional[List[str]] = Field(default_factory=list)
    reason: Optional[str] = None

class RoleChangeRequestInDB(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    user_id: str
    role: UserRole
    requested_role: UserRole
    email: EmailStr
    domains_to_observe: List[str] = Field(default_factory=list)
    reason: Optional[str] = None
    status: str = Field(default="pending") # "pending", "approved", "rejected"
    admin_notes: Optional[str] = None
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None

    @validator("id", pre=True)
    def convert_objectid_to_str(cls, v):
        return str(v) if isinstance(v, ObjectId) else v

class UserWithRoleRequests(UserInfo):
    role_change_requests: Optional[RoleChangeRequestInDB] = None

class ApproveAccountSchema(BaseModel):
    approved_by_admin: bool
