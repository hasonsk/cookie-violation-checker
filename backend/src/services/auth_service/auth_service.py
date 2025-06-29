from passlib.context import CryptContext
from typing import Any, Dict, Optional, List
from pydantic import EmailStr
import secrets
from datetime import datetime, timedelta

from src.schemas.auth import (
    RegisterSchema,
    RegisterResponseSchema,
    LoginSchema,
    LoginResponseSchema,
    ForgotPasswordRequestSchema,
    ResetPasswordRequestSchema,
    MessageResponseSchema,
)
from src.schemas.user import User # Import User
from src.models.user import User as UserModel, UserRole # Alias User from models to avoid conflict
from src.models.domain_request import DomainRequest
from src.utils.jwt_handler import create_access_token, decode_access_token
from src.configs.settings import settings

from src.exceptions.custom_exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    UnauthorizedError,
    UserNotFoundError,
    InvalidTokenError,
    TokenExpiredError
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
        # Ensure all fields, including those with default values, are included
        await self.user_repo.create_user(new_user.model_dump(by_alias=True, exclude_unset=False, exclude_defaults=False))
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

    async def request_password_reset(self, email: EmailStr) -> MessageResponseSchema:
        user_data = await self.user_repo.get_user_by_email(email)
        if not user_data:
            raise UserNotFoundError()

        user = UserModel.parse_obj(user_data)
        reset_token = secrets.token_urlsafe(32)
        reset_token_expires = datetime.utcnow() + timedelta(minutes=settings.app.RESET_TOKEN_EXPIRE_MINUTES)

        await self.user_repo.update_user(
            user.id,
            {"reset_token": reset_token, "reset_token_expires": reset_token_expires}
        )

        # In a real application, you would send an email here.
        # For now, we'll just return a success message.
        print(f"Password reset token for {email}: {reset_token}")
        return MessageResponseSchema(message="Yêu cầu đặt lại mật khẩu đã được gửi. Vui lòng kiểm tra email của bạn.")

    async def reset_password(self, token: str, new_password: str) -> MessageResponseSchema:
        user_data = await self.user_repo.get_user_by_reset_token(token)
        if not user_data:
            raise InvalidTokenError()

        user = UserModel.parse_obj(user_data)

        if user.reset_token_expires and user.reset_token_expires < datetime.utcnow():
            # Clear expired token
            await self.user_repo.update_user(
                user.id,
                {"reset_token": None, "reset_token_expires": None}
            )
            raise TokenExpiredError()

        hashed_password = pwd_context.hash(new_password)
        await self.user_repo.update_user(
            user.id,
            {"password": hashed_password, "reset_token": None, "reset_token_expires": None}
        )
        return MessageResponseSchema(message="Mật khẩu của bạn đã được đặt lại thành công.")
