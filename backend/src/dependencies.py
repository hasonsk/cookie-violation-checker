from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo.collection import Collection
from repositories.user_repository import UserRepository
from services.auth_service.auth_service import AuthService
from configs.database import get_collection
from configs.app_settings import USERS_COLLECTION
from utils.jwt_handler import decode_access_token
from schemas.auth_schema import UserInfo, UserRole
from exceptions.custom_exceptions import UnauthorizedError, UserNotFoundError

oauth2_scheme = HTTPBearer()

def get_user_repository(
    users_collection: Collection = Depends(lambda: get_collection(USERS_COLLECTION))
) -> UserRepository:
    return UserRepository(users_collection)

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthService:
    return AuthService(user_repo)

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserInfo:
    try:
        payload = decode_access_token(token.credentials)
        if payload is None:
            raise UnauthorizedError("Invalid token")
        email = payload.get("sub")
        if email is None:
            raise UnauthorizedError("Invalid token payload")
        user = await auth_service.get_current_user(email)
        if not user:
            raise UserNotFoundError("User not found")
        return user
    except (UnauthorizedError, UserNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_admin_or_manager(current_user: UserInfo = Depends(get_current_user)) -> UserInfo:
    if current_user.role not in [UserRole.admin, UserRole.cmp_manager]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
