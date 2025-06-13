from pydantic import BaseModel, EmailStr
from .user import UserInfo

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class LoginResponseSchema(BaseModel):
    token: str
    user: UserInfo

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

class RegisterResponseSchema(BaseModel):
    msg: str
