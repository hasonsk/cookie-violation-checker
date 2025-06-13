from enum import Enum
from pydantic import BaseModel

class UserRole(str, Enum):
  admin = "admin"
  user = "user"
  guest = "guest"

class UserInfo(BaseModel):
  email: str
  password: str
  name: str
  role: UserRole
  company_name: str
