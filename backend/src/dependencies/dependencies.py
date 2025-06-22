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
from src.repositories.website_repository import WebsiteRepository

from src.configs.settings import settings

from src.services.auth_service.auth_service import AuthService
from src.services.cookie_extractor_service.policy_cookie_extractor_service import CookieExtractorService
from src.services.cookie_extractor_service.interfaces.llm_provider import ILLMProvider
from src.services.cookie_extractor_service.factories.cookie_extractor_factory import CookieExtractorFactory, LLMProviderType
from src.services.cookie_extractor_service.processors.content_analyzer import ContentAnalyzer
from src.services.cookie_extractor_service.processors.prompt_builder import PromptBuilder
from src.services.cookie_extractor_service.processors.response_processor import LLMResponseProcessor
from src.services.policy_crawler_service.policy_crawler_service import PolicyCrawlerService
from src.services.policy_crawler_service.crawler_factory import CrawlerFactory
from src.services.comparator_service.comparator_factory import ComparatorFactory
from src.services.comparator_service.components.compliance_comparator import ComplianceComparator
from src.services.comparator_service.comparator_service import ComparatorService
from src.services.violation_analyzer_service.violation_analyzer_service import ViolationAnalyzerService
from src.services.domain_request_service import DomainRequestService
from src.services.website_management_service.website_management_service import WebsiteManagementService
# from src.services.reporter_service.reporter_service import ReporterService

from src.utils.jwt_handler import decode_access_token
from src.schemas.user import User, UserRole
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

def get_llm_provider() -> ILLMProvider:
    return CookieExtractorFactory.create_provider(
        provider_type=LLMProviderType.GEMINI,
        # provider_type=LLMProviderType.LLAMA,
        api_key=settings.external.GEMINI_API_KEY,
        # api_endpoint=settings.external.LLAMA_API_ENDPOINT,
        model=settings.external.GEMINI_MODEL,
        temperature=settings.external.TEMPERATURE,
        max_tokens=settings.external.MAX_OUTPUT_TOKENS
    )

def get_content_analyzer() -> ContentAnalyzer:
    return ContentAnalyzer()

def get_prompt_builder() -> PromptBuilder:
    return PromptBuilder(system_prompt=settings.llm.SYSTEM_PROMPT_GEMINI)

def get_response_processor() -> LLMResponseProcessor:
    return LLMResponseProcessor()

def get_policy_cookie_extractor_service(
    llm_provider: ILLMProvider = Depends(get_llm_provider),
    content_analyzer: ContentAnalyzer = Depends(get_content_analyzer),
    prompt_builder: PromptBuilder = Depends(get_prompt_builder),
    response_processor: LLMResponseProcessor = Depends(get_response_processor),
    cookie_feature_repository: CookieFeatureRepository = Depends(get_cookie_feature_repository)
) -> CookieExtractorService:
    return CookieExtractorService(
        llm_provider=llm_provider,
        content_analyzer=content_analyzer,
        prompt_builder=prompt_builder,
        response_processor=response_processor,
        cookie_feature_repository=cookie_feature_repository
    )

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

def get_compliance_comparator() -> ComplianceComparator:
    return ComplianceComparator()

def get_comparator_service(
    violation_repository: ViolationRepository = Depends(get_violation_repository),
    compliance_analyzer: ComplianceComparator = Depends(get_compliance_comparator),
) -> ComparatorService:
    return ComparatorFactory.create_comparator(violation_repository, compliance_analyzer)

def get_website_repository() -> WebsiteRepository:
    return WebsiteRepository()

def get_domain_request_repository() -> DomainRequestRepository:
    return DomainRequestRepository()

def get_domain_request_service(
    domain_request_repo: DomainRequestRepository = Depends(get_domain_request_repository),
    website_repo: WebsiteRepository = Depends(get_website_repository)
) -> DomainRequestService:
    return DomainRequestService(domain_request_repo, website_repo)

def get_violation_analyzer_service(
    policy_crawler: PolicyCrawlerService = Depends(create_playwright_bing_extractor),
    policy_cookie_extractor_service: CookieExtractorService = Depends(get_policy_cookie_extractor_service),
    comparator_service: ComparatorService = Depends(get_comparator_service),
    violation_repository: ViolationRepository = Depends(get_violation_repository),
    website_repository: WebsiteRepository = Depends(get_website_repository)
) -> ViolationAnalyzerService:
    return ViolationAnalyzerService(
        policy_crawler=policy_crawler,
        policy_cookie_extractor_service=policy_cookie_extractor_service,
        comparator_service=comparator_service,
        violation_repository=violation_repository,
        website_repository=website_repository
    )

def get_website_management_service(
    website_repo: WebsiteRepository = Depends(get_website_repository),
    violation_repo: ViolationRepository = Depends(get_violation_repository)
) -> WebsiteManagementService:
    return WebsiteManagementService(website_repo, violation_repo)

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    role_change_request_repo: DomainRequestRepository = Depends(get_role_change_request_repository)
) -> AuthService:
    return AuthService(user_repo, role_change_request_repo)

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    try:
        payload = decode_access_token(token.credentials)
        if payload is None:
            raise UnauthorizedError("Invalid token")
        user_id = payload.get("sub")
        if user_id is None:
            raise UnauthorizedError("Invalid token payload")
        user_data = await auth_service.get_current_user(user_id)
        if not user_data:
            raise UserNotFoundError()
        return User(**user_data.model_dump()) # Convert to dict then to User
    except (UnauthorizedError, UserNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_admin_or_manager(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
