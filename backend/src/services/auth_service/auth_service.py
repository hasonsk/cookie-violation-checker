from repositories.user_repository import UserRepository
from passlib.context import CryptContext
from utils.jwt_handler import create_access_token, decode_access_token
from schemas.auth_schema import RegisterSchema, LoginSchema
from schemas.auth_schema import RegisterResponseSchema, LoginResponseSchema, UserInfo
from exceptions.custom_exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    UnauthorizedError,
    UserNotFoundError
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, data: RegisterSchema) -> RegisterResponseSchema:
        existing = await self.user_repo.get_user_by_email(data.email)
        if existing:
            raise EmailAlreadyExistsError()

        hashed = pwd_context.hash(data.password)
        new_user = {
            "name": data.name,
            "email": data.email,
            "password": hashed
        }
        await self.user_repo.create_user(new_user)
        return RegisterResponseSchema(msg="Đăng ký thành công")

    async def login_user(self, data: LoginSchema) -> LoginResponseSchema:
        user = await self.user_repo.get_user_by_email(data.email)
        if not user or not pwd_context.verify(data.password, user["password"]):
            raise InvalidCredentialsError()

        token = create_access_token({"sub": user["email"]})
        return LoginResponseSchema(
            token=token,
            user={
                "name": user["name"],
                "email": user["email"]
            }
        )

    async def get_current_user(self, token: str) -> UserInfo:
        payload = decode_access_token(token)
        if payload is None:
            raise UnauthorizedError()
        email = payload.get("sub")
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise UserNotFoundError()
        return UserInfo(
            name=user["name"],
            email=user["email"]
        )
