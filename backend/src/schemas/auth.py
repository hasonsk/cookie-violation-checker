from pydantic import BaseModel, EmailStr
from typing import Optional
from .user import User, UserRole # Import User and UserRole enum

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class LoginResponseSchema(BaseModel):
    token: str
    user: User

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole # Thêm trường này

class RegisterResponseSchema(BaseModel):
    msg: str

class ForgotPasswordRequestSchema(BaseModel):
    email: EmailStr

class ResetPasswordRequestSchema(BaseModel):
    token: str
    new_password: str

class MessageResponseSchema(BaseModel):
    message: str
