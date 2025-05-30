from pydantic import BaseModel, EmailStr

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    name: str
    email: EmailStr

class TokenResponse(BaseModel):
    token: str
    user: UserOut
