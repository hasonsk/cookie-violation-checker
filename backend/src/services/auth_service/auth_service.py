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
    UserInfo
)
from src.models.user import User, UserRole
from src.models.domain_request import DomainRequest
from src.utils.jwt_handler import create_access_token, decode_access_token

from src.exceptions.custom_exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    UnauthorizedError,
    UserNotFoundError
)
from src.repositories.user_repository import UserRepository
from repositories.domain_request_repository import DomainRequestRepository


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
            password=hashed
        )
        await self.user_repo.create_user(new_user)
        return RegisterResponseSchema(msg="Đăng ký thành công")

    async def login_user(self, data: LoginSchema) -> LoginResponseSchema:
        user_data = await self.user_repo.get_user_by_email(data.email)
        if not user_data or not pwd_context.verify(data.password, user_data["password"]):
            raise InvalidCredentialsError()

        user = User.parse_obj(user_data)
        token = create_access_token({"sub": str(user.id)})
        return LoginResponseSchema(
            token=token,
            user=UserInfo(
                id=str(user.id),
                name=user.name,
                email=user.email,
                role=user.role,
                approved_by_admin=user.approved_by_admin
            )
        )

    async def get_current_user(self, user_id: str) -> UserInfo:
        user_data = await self.user_repo.get_user_by_id(user_id)
        if not user_data:
            raise UserNotFoundError()
        user = User.parse_obj(user_data)
        return UserInfo.parse_obj(user)

    async def approve_account(self, user_id: str, current_user: UserInfo) -> Optional[UserInfo]:
        if current_user.role not in [UserRole.ADMIN, UserRole.cmp_manager]:
            raise UnauthorizedError("Only admins or CMP managers can approve accounts.")

        user_data = await self.user_repo.get_user_by_id(user_id)
        if not user_data:
            raise UserNotFoundError()

        updated_user_data = await self.user_repo.approve_account(user_id)
        if updated_user_data:
            updated_user = User.parse_obj(updated_user_data)
            return UserInfo(
                id=str(updated_user.id),
                name=updated_user.name,
                email=updated_user.email,
                role=updated_user.role,
                approved_by_admin=updated_user.approved_by_admin
            )
        return None

    async def approve_role_change(self, user_id: str, current_user: UserInfo) -> Optional[UserInfo]:
        if current_user.role not in [UserRole.ADMIN, UserRole.cmp_manager]:
            raise UnauthorizedError("Only admins or CMP managers can approve role changes.")

        user_data = await self.user_repo.get_user_by_id(user_id)
        if not user_data:
            raise UserNotFoundError()
        user = User.parse_obj(user_data)
        if not user.requested_role:
            raise ValueError("No role change request pending for this user.")

        updated_user_data = await self.user_repo.approve_role_change(user_id)
        if updated_user_data:
            updated_user = User.parse_obj(updated_user_data)
            return UserInfo(
                id=str(updated_user.id),
                name=updated_user.name,
                email=updated_user.email,
                role=updated_user.role,
                approved_by_admin=updated_user.approved_by_admin
            )
        return None
