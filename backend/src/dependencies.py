from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo.collection import Collection # Keep this if other dependencies still need it, otherwise remove

from src.repositories.user_repository import UserRepository
from src.repositories.role_change_request_repository import RoleChangeRequestRepository
from src.repositories.policy_content_repository import PolicyContentRepository
from src.repositories.discovery_repo import PolicyDiscoveryRepository
from src.repositories.cookie_repo import CookieFeatureRepository
from src.repositories.violation_repo import ViolationRepository

from src.services.auth_service.auth_service import AuthService
from src.services.policy_extract_service.policy_extract_service import PolicyExtractService
from src.services.policy_discover_service.policy_discovery_service import PolicyDiscoveryService
from src.services.cookies_extract_service.cookies_extractor import CookieExtractorService
from src.services.violation_detect_service.violation_detector_service import ViolationDetectorService
from src.controllers.policy_extract_controller import PolicyExtractController
from src.utils.jwt_handler import decode_access_token
from src.schemas.auth_schema import UserInfo, UserRole
from src.exceptions.custom_exceptions import UnauthorizedError, UserNotFoundError

oauth2_scheme = HTTPBearer()

def get_user_repository() -> UserRepository:
    return UserRepository()

def get_role_change_request_repository() -> RoleChangeRequestRepository:
    return RoleChangeRequestRepository()

def get_policy_discovery_repository() -> PolicyDiscoveryRepository:
    return PolicyDiscoveryRepository()

def get_policy_content_repository() -> PolicyContentRepository:
    return PolicyContentRepository()

def get_cookie_feature_repository() -> CookieFeatureRepository:
    return CookieFeatureRepository()

def get_violation_repository() -> ViolationRepository:
    return ViolationRepository()

async def get_policy_discovery_service(
    policy_discovery_repo: PolicyDiscoveryRepository = Depends(get_policy_discovery_repository)
) -> PolicyDiscoveryService:
    async with PolicyDiscoveryService(policy_discovery_repo) as service:
        yield service

def get_policy_extract_service(
    policy_repository: PolicyContentRepository = Depends(get_policy_content_repository)
) -> PolicyExtractService:
    return PolicyExtractService(policy_repository)

def get_cookie_extractor_service() -> CookieExtractorService:
    return CookieExtractorService()

def get_violation_detector_service(
    violation_repo: ViolationRepository = Depends(get_violation_repository)
) -> ViolationDetectorService:
    return ViolationDetectorService()

def get_policy_extract_controller(
    policy_extract_service: PolicyExtractService = Depends(get_policy_extract_service)
) -> PolicyExtractController:
    return PolicyExtractController(policy_extract_service)

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    role_change_request_repo: RoleChangeRequestRepository = Depends(get_role_change_request_repository)
) -> AuthService:
    return AuthService(user_repo, role_change_request_repo)

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserInfo:
    try:
        payload = decode_access_token(token.credentials)
        if payload is None:
            raise UnauthorizedError("Invalid token")
        user_id = payload.get("sub")
        if user_id is None:
            raise UnauthorizedError("Invalid token payload")
        user = await auth_service.get_current_user(user_id)
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
