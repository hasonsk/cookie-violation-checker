from pydantic import BaseModel, EmailStr

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class RegisterResponseSchema(BaseModel):
    msg: str

class UserInfo(BaseModel):
    name: str
    email: EmailStr

class LoginResponseSchema(BaseModel):
    token: str
    user: UserInfo
