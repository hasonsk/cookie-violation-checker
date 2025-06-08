from passlib.context import CryptContext
from typing import Any, Dict, Optional, List
from pydantic import EmailStr

from src.schemas.auth_schema import (
    RegisterSchema,
    LoginSchema,
    RegisterResponseSchema,
    LoginResponseSchema,
    UserInfo,
    User,
    UserRole,
    RequestRoleChangePayloadSchema,
    RoleChangeRequestInDB,
    UserWithRoleRequests
)
from src.utils.jwt_handler import create_access_token, decode_access_token

from src.exceptions.custom_exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    UnauthorizedError,
    UserNotFoundError
)
from src.repositories.user_repository import UserRepository
from src.repositories.role_change_request_repository import RoleChangeRequestRepository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, user_repo: UserRepository, role_change_request_repo: RoleChangeRequestRepository):
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
        user = await self.user_repo.get_user_by_email(data.email)
        if not user or not pwd_context.verify(data.password, user["password"]):
            raise InvalidCredentialsError()

        token = create_access_token({"sub": str(user["_id"])})
        return LoginResponseSchema(
            token=token,
            user=UserInfo(
                id=str(user["_id"]),
                name=user["name"],
                email=user["email"],
                role=UserRole(user["role"]) if user["role"] in [role for role in UserRole] else UserRole.unregistered,
                approved_by_admin=user["approved_by_admin"]
            )
        )

    async def get_current_user(self, user_id: str) -> UserInfo:
        user = await self.user_repo.get_user_by_id(user_id)
        print("--> USER: ", user["_id"])
        if not user:
            raise UserNotFoundError()
        return UserInfo.parse_obj(user)

    async def request_role_change(self, user_id: str, current_user_email: EmailStr, current_user_role: UserRole, requested_role_data: RequestRoleChangePayloadSchema) -> RoleChangeRequestInDB:
        if current_user_role != UserRole.unregistered:
            raise UnauthorizedError("Only unregistered users can request a role change.")
        if requested_role_data.requested_role != UserRole.provider:
            raise ValueError("Role change can only be requested to 'provider'.")

        # Check if there's an existing pending request for this user
        existing_request = await self.role_change_request_repo.get_request_by_user_id(user_id)
        if existing_request:
            raise ValueError("A pending role change request already exists for this user.")

        new_request = RoleChangeRequestInDB(
            user_id=user_id,
            role=current_user_role,
            requested_role=requested_role_data.requested_role,
            email=current_user_email,
            domains_to_observe=requested_role_data.domains_to_observe,
            reason=requested_role_data.reason,
            status="pending"
        )
        request_id = await self.role_change_request_repo.create_role_change_request(new_request)
        new_request.id = request_id # Assign the ID returned from the database
        return new_request

    async def get_all_users(self, filters: Optional[Dict[str, Any]] = None) -> List[UserWithRoleRequests]:
        """Get all users, optionally filtered, and return as UserWithRoleRequests, including role change requests."""
        users_data = await self.user_repo.get_all_users(filters)

        users_with_requests = []
        for user in users_data:
            print(user)
            print(type(user["_id"]))
            user_info = UserInfo.parse_obj(user)
            print(user_info)


            role_requests_data = await self.role_change_request_repo.get_request_by_user_id(str(user["_id"]))
            role_requests = RoleChangeRequestInDB.parse_obj(role_requests_data) if role_requests_data else None

            users_with_requests.append(
                UserWithRoleRequests(
                    **user_info.dict(by_alias=True),
                    role_change_requests=role_requests
                )
            )
        print("USERS_WITH_REQUEST: ", users_with_requests)
        return users_with_requests

    async def approve_account(self, user_id: str, current_user: UserInfo) -> Optional[UserInfo]:
        if current_user.role not in [UserRole.admin, UserRole.cmp_manager]:
            raise UnauthorizedError("Only admins or CMP managers can approve accounts.")

        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        updated_user = await self.user_repo.approve_account(user_id)
        if updated_user:
            return UserInfo(
                id=str(updated_user["_id"]),
                name=updated_user["name"],
                email=updated_user["email"],
                role=UserRole(updated_user["role"]),
                approved_by_admin=updated_user["approved_by_admin"]
            )
        return None

    async def approve_role_change(self, user_id: str, current_user: UserInfo) -> Optional[UserInfo]:
        if current_user.role not in [UserRole.admin, UserRole.cmp_manager]:
            raise UnauthorizedError("Only admins or CMP managers can approve role changes.")

        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        if not user.get("requested_role"):
            raise ValueError("No role change request pending for this user.")

        updated_user = await self.user_repo.approve_role_change(user_id)
        if updated_user:
            return UserInfo(
                id=str(updated_user["_id"]),
                name=updated_user["name"],
                email=updated_user["email"],
                role=UserRole(updated_user["role"]),
                approved_by_admin=updated_user["approved_by_admin"]
            )
        return None
