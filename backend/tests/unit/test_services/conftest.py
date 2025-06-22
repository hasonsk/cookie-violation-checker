import pytest
from unittest.mock import AsyncMock, MagicMock

# Import all services and repositories that might be mocked in unit tests
from src.services.violation_analyzer_service.violation_analyzer_service import ViolationAnalyzerService
from src.services.policy_crawler_service.policy_crawler_service import PolicyCrawlerService
from src.services.cookie_extractor_service.policy_cookie_extractor_service import CookieExtractorService
from src.services.comparator_service.comparator_service import ComparatorService

from src.repositories.violation_repository import ViolationRepository
from src.repositories.website_repository import WebsiteRepository
from src.repositories.policy_content_repository import PolicyContentRepository
from src.repositories.policy_storage_repository import PolicyStorageService
from src.repositories.cookie_feature_repository import CookieFeatureRepository

from src.services.policy_crawler_service.interfaces.content_extractor_interface import IContentExtractor
from src.services.policy_crawler_service.interfaces.search_provider_interface import ISearchProvider
from src.services.policy_crawler_service.components.link_discovery import LinkDiscovery
from src.services.policy_crawler_service.components.content_processor import ContentProcessor

from src.services.cookie_extractor_service.interfaces.llm_provider import ILLMProvider
from src.services.cookie_extractor_service.processors.content_analyzer import ContentAnalyzer
from src.services.cookie_extractor_service.processors.prompt_builder import PromptBuilder
from src.services.cookie_extractor_service.processors.response_processor import LLMResponseProcessor

from src.services.comparator_service.interfaces.compliance_analyzer import IComplianceAnalyzer
from src.services.comparator_service.interfaces.compliance_result import IComplianceResultBuilder
from src.services.comparator_service.interfaces.cookie_data_processor import ICookieDataProcessor
from src.services.comparator_service.interfaces.violation_persister import IViolationPersister
from src.utils.url_utils import get_base_url # For domain_extractor mock

# --- Fixtures for ViolationAnalyzerService dependencies ---
@pytest.fixture
def mock_policy_crawler():
    return AsyncMock(spec=PolicyCrawlerService)

@pytest.fixture
def mock_cookie_extractor_service():
    return AsyncMock(spec=CookieExtractorService)

@pytest.fixture
def mock_comparator_service():
    return AsyncMock(spec=ComparatorService)

@pytest.fixture
def mock_violation_repository():
    return AsyncMock(spec=ViolationRepository)

@pytest.fixture
def mock_website_repository():
    return AsyncMock(spec=WebsiteRepository)

# --- Fixtures for PolicyCrawlerService dependencies ---
@pytest.fixture
def mock_discovery_service():
    return AsyncMock(spec=LinkDiscovery)

@pytest.fixture
def mock_content_extractor():
    return AsyncMock(spec=IContentExtractor)

@pytest.fixture
def mock_search_provider():
    return AsyncMock(spec=ISearchProvider)

@pytest.fixture
def mock_content_processor():
    return AsyncMock(spec=ContentProcessor)

@pytest.fixture
def mock_policy_storage_repository():
    return AsyncMock(spec=PolicyStorageService)

# --- Fixtures for CookieExtractorService dependencies ---
@pytest.fixture
def mock_llm_provider():
    return AsyncMock(spec=ILLMProvider)

@pytest.fixture
def mock_content_analyzer():
    return MagicMock(spec=ContentAnalyzer)

@pytest.fixture
def mock_prompt_builder():
    return MagicMock(spec=PromptBuilder)

@pytest.fixture
def mock_response_processor():
    return MagicMock(spec=LLMResponseProcessor)

@pytest.fixture
def mock_cookie_feature_repository():
    return AsyncMock(spec=CookieFeatureRepository)

# --- Fixtures for ComparatorService dependencies ---
@pytest.fixture
def mock_cookie_data_processor():
    return MagicMock(spec=ICookieDataProcessor)

@pytest.fixture
def mock_compliance_analyzer():
    return MagicMock(spec=IComplianceAnalyzer)

@pytest.fixture
def mock_compliance_result_builder():
    return MagicMock(spec=IComplianceResultBuilder)

@pytest.fixture
def mock_violation_persister():
    return AsyncMock(spec=IViolationPersister)

@pytest.fixture
def mock_domain_extractor():
    return MagicMock(side_effect=get_base_url) # Use the actual utility function for simplicity in mock
