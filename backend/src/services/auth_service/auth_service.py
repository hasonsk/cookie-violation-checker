from passlib.context import CryptContext
from typing import Any, Dict, Optional, List
from pydantic import EmailStr

from src.schemas.auth import (
    RegisterSchema,
    RegisterResponseSchema,
)
from src.schemas.auth import (
    LoginSchema,
    LoginResponseSchema,
)
from src.schemas.user import User # Import User
from src.models.user import User as UserModel, UserRole # Alias User from models to avoid conflict
from src.models.domain_request import DomainRequest
from src.utils.jwt_handler import create_access_token, decode_access_token

from src.exceptions.custom_exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    UnauthorizedError,
    UserNotFoundError
)
from src.repositories.user_repository import UserRepository
from src.repositories.domain_request_repository import DomainRequestRepository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, user_repo: UserRepository, role_change_request_repo: DomainRequestRepository):
        self.user_repo = user_repo
        self.role_change_request_repo = role_change_request_repo

    async def register_user(self, data: RegisterSchema) -> RegisterResponseSchema:
        existing = await self.user_repo.get_user_by_email(data.email)
        if existing:
            raise EmailAlreadyExistsError()

        hashed = pwd_context.hash(data.password)
        new_user = User(
            name=data.name,
            email=data.email,
            password=hashed,
            role=data.role, # Lưu vai trò người dùng chọn
            approved_by_admin=False # Luôn đặt là False khi đăng ký
        )
        # Sửa lại user.dict() thành new_user.model_dump() theo Pydantic v2
        await self.user_repo.create_user(new_user.model_dump())
        return RegisterResponseSchema(msg="Đăng ký thành công. Vui lòng chờ quản trị viên phê duyệt.")

    async def login_user(self, data: LoginSchema) -> LoginResponseSchema:
        user_data = await self.user_repo.get_user_by_email(data.email)
        if not user_data or not pwd_context.verify(data.password, user_data["password"]):
            raise InvalidCredentialsError()

        user = UserModel.parse_obj(user_data)
        token = create_access_token({"sub": str(user.id)})
        return LoginResponseSchema(
            token=token,
            user=User(
                id=str(user.id),
                name=user.name,
                email=user.email,
                role=user.role,
                approved_by_admin=user.approved_by_admin,
                company_name=user.company_name # Ensure company_name is included
            )
        )

    async def get_current_user(self, user_id: str) -> User:
        user_data = await self.user_repo.get_user_by_id(user_id)
        if not user_data:
            raise UserNotFoundError()
        user = User(**user_data) # Directly create User from user_data
        return user
