from concurrent.futures import ThreadPoolExecutor
from playwright.async_api import async_playwright
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.utils.cache_utils import CacheManager
from src.utils.dom_parser_utils import DOMParserService
from src.utils.table_extractor import TableExtractor
from src.utils.text_processing import TextProcessor
from src.utils.translation_utils import TranslationManager
from src.repositories.user_repository import UserRepository
from src.repositories.domain_request_repository import DomainRequestRepository
from src.repositories.policy_content_repository import PolicyContentRepository
from src.repositories.cookie_feature_repository import CookieFeatureRepository
from src.repositories.violation_repository import ViolationRepository
# from src.repositories.website_repository import WebsiteRepository

from src.configs.settings import settings

from src.services.auth_service.auth_service import AuthService
from src.services.llm_services.policy_llm_service import PolicyLLMService, GeminiService # Import GeminiService
from src.repositories.policy_content_repository import PolicyContentRepository
from src.services.policy_crawler_service.policy_crawler_service import PolicyCrawlerService
from src.services.policy_crawler_service.crawler_factory import CrawlerFactory
from src.services.comparator_service.comparator_service import ComparatorService
from src.services.violation_analyzer_service.violation_analyzer_service import ViolationAnalyzerService
# from src.services.website_management_service.website_management_service import WebsiteManagementService
# from src.services.reporter_service.reporter_service import ReporterService

from src.utils.jwt_handler import decode_access_token
from src.schemas.user import UserInfo, UserRole
from src.exceptions.custom_exceptions import UnauthorizedError, UserNotFoundError

oauth2_scheme = HTTPBearer()

def get_user_repository() -> UserRepository:
    return UserRepository()

def get_role_change_request_repository() -> DomainRequestRepository:
    return DomainRequestRepository()

def get_policy_content_repository() -> PolicyContentRepository:
    return PolicyContentRepository()

def get_cookie_feature_repository() -> CookieFeatureRepository:
    return CookieFeatureRepository()

def get_violation_repository() -> ViolationRepository:
    return ViolationRepository()

def get_gemini_service() -> GeminiService:
    return GeminiService()

def get_policy_extractor_service(
    gemini_service: GeminiService = Depends(get_gemini_service)
) -> PolicyLLMService:
    return PolicyLLMService(gemini_service)

async def create_playwright_bing_extractor(
    policy_content_repo: PolicyContentRepository = Depends(get_policy_content_repository)
) -> PolicyCrawlerService:
    """
    Provides a PolicyCrawlerService instance with a Playwright-based content extractor.
    Manages the Playwright browser and context lifecycle.
    """
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=True)
    context = await browser.new_context()
    try:
        yield CrawlerFactory.create_playwright_bing_extractor(
            policy_content_repo=policy_content_repo,
            browser_context=context,
            timeout=30
        )
    finally:
        await context.close()
        await browser.close()
        await p.stop()

def get_comparator_service(
    violation_repository: ViolationRepository = Depends(get_violation_repository)
) -> ComparatorService:
    return ComparatorService(violation_repository)

def get_violation_analyzer_service(
    policy_crawler: PolicyCrawlerService = Depends(create_playwright_bing_extractor),
    policy_extractor_service: PolicyLLMService = Depends(get_policy_extractor_service), # Keep this for LLM extraction
    comparator_service: ComparatorService = Depends(get_comparator_service),
    violation_repository: ViolationRepository = Depends(get_violation_repository)
) -> ViolationAnalyzerService:
    return ViolationAnalyzerService(
        policy_crawler=policy_crawler,
        policy_extractor_service=policy_extractor_service,
        comparator_service=comparator_service,
        violation_repository=violation_repository
    )

# def get_website_management_service(
#     website_repo: WebsiteRepository = Depends(get_website_repository)
# ) -> WebsiteManagementService:
#     return WebsiteManagementService(website_repo)

# def get_reporter_service(
#     violation_repo: ViolationRepository = Depends(get_violation_repository)
# ) -> ReporterService:
#     return ReporterService(violation_repo)

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    role_change_request_repo: DomainRequestRepository = Depends(get_role_change_request_repository)
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
    if current_user.role not in [UserRole.ADMIN, UserRole.cmp_manager]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
