import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Optional

from src.services.policy_crawler_service.policy_crawler_service import PolicyCrawlerService
from src.services.policy_crawler_service.interfaces.content_extractor_interface import IContentExtractor
from src.services.policy_crawler_service.interfaces.search_provider_interface import ISearchProvider
from src.services.policy_crawler_service.components.link_discovery import LinkDiscovery
from src.services.policy_crawler_service.components.content_processor import ContentProcessor
from src.repositories.policy_storage_repository import PolicyStorageService
from src.schemas.policy import PolicyContent

# Mock data
MOCK_WEB_URL = "https://example.com"
MOCK_ROOT_URL = "https://example.com"
MOCK_POLICY_URL_DISCOVERY = "https://example.com/privacy"
MOCK_POLICY_URL_SEARCH = "https://example.com/cookie-policy"
MOCK_HTML_CONTENT = "<html><body><h1>Cookie Policy</h1><p>This is a test policy.</p></body></html>"
MOCK_POLICY_CONTENT_OBJ = PolicyContent(
    website_url=MOCK_ROOT_URL,
    policy_url=MOCK_POLICY_URL_DISCOVERY,
    original_content=MOCK_HTML_CONTENT,
    detected_language="en",
    table_content=[],
    translated_content=None, # Added missing field
    translated_table_content=None # Added missing field
)

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
def mock_storage_repository():
    return AsyncMock(spec=PolicyStorageService)

@pytest.fixture
def policy_crawler_service(
    mock_discovery_service,
    mock_content_extractor,
    mock_search_provider,
    mock_content_processor,
    mock_storage_repository
):
    return PolicyCrawlerService(
        discovery_service=mock_discovery_service,
        content_extractor=mock_content_extractor,
        search_provider=mock_search_provider,
        content_processor=mock_content_processor,
        storage_repository=mock_storage_repository
    )

@pytest.mark.asyncio
async def test_extract_policy_success_from_discovery(
    policy_crawler_service,
    mock_discovery_service,
    mock_content_extractor,
    mock_search_provider,
    mock_content_processor,
    mock_storage_repository
):
    """
    Test policy extraction when link is found via LinkDiscovery.
    """
    mock_storage_repository.get_existing_policy.return_value = None
    mock_discovery_service.discover_policy_link.return_value = MOCK_POLICY_URL_DISCOVERY
    mock_content_extractor.extract_content.return_value = MOCK_HTML_CONTENT
    mock_content_processor.process_content.return_value = MOCK_POLICY_CONTENT_OBJ
    mock_storage_repository.save_policy.return_value = None

    result = await policy_crawler_service.extract_policy(MOCK_WEB_URL)

    mock_storage_repository.get_existing_policy.assert_called_once_with(MOCK_ROOT_URL)
    mock_discovery_service.discover_policy_link.assert_called_once_with(MOCK_ROOT_URL)
    mock_search_provider.search_policy.assert_not_called() # Should not be called
    mock_content_extractor.extract_content.assert_called_once_with(MOCK_POLICY_URL_DISCOVERY)
    mock_content_processor.process_content.assert_called_once()
    mock_storage_repository.save_policy.assert_called_once()

    assert result == MOCK_POLICY_CONTENT_OBJ

@pytest.mark.asyncio
async def test_extract_policy_success_from_search(
    policy_crawler_service,
    mock_discovery_service,
    mock_content_extractor,
    mock_search_provider,
    mock_content_processor,
    mock_storage_repository
):
    """
    Test policy extraction when link is found via SearchProvider (fallback).
    """
    mock_storage_repository.get_existing_policy.return_value = None
    mock_discovery_service.discover_policy_link.return_value = None # No link found via discovery
    mock_search_provider.search_policy.return_value = MOCK_POLICY_URL_SEARCH
    mock_content_extractor.extract_content.return_value = MOCK_HTML_CONTENT
    mock_content_processor.process_content.return_value = PolicyContent(
        website_url=MOCK_ROOT_URL,
        policy_url=MOCK_POLICY_URL_SEARCH, # Updated policy_url
        original_content=MOCK_HTML_CONTENT,
        detected_language="en",
        table_content=[],
        translated_content=None, # Added missing field
        translated_table_content=None # Added missing field
    )
    mock_storage_repository.save_policy.return_value = None

    result = await policy_crawler_service.extract_policy(MOCK_WEB_URL)

    mock_storage_repository.get_existing_policy.assert_called_once_with(MOCK_ROOT_URL)
    mock_discovery_service.discover_policy_link.assert_called_once_with(MOCK_ROOT_URL)
    mock_search_provider.search_policy.assert_called_once_with(MOCK_ROOT_URL)
    mock_content_extractor.extract_content.assert_called_once_with(MOCK_POLICY_URL_SEARCH)
    mock_content_processor.process_content.assert_called_once()
    mock_storage_repository.save_policy.assert_called_once()

    assert result.policy_url == MOCK_POLICY_URL_SEARCH
    assert result.original_content == MOCK_HTML_CONTENT

@pytest.mark.asyncio
async def test_extract_policy_not_found(
    policy_crawler_service,
    mock_discovery_service,
    mock_search_provider,
    mock_storage_repository
):
    """
    Test policy extraction when no policy link is found at all.
    """
    mock_storage_repository.get_existing_policy.return_value = None
    mock_discovery_service.discover_policy_link.return_value = None
    mock_search_provider.search_policy.return_value = None

    result = await policy_crawler_service.extract_policy(MOCK_WEB_URL)

    mock_storage_repository.get_existing_policy.assert_called_once_with(MOCK_ROOT_URL)
    mock_discovery_service.discover_policy_link.assert_called_once_with(MOCK_ROOT_URL)
    mock_search_provider.search_policy.assert_called_once_with(MOCK_ROOT_URL)
    assert result is None

@pytest.mark.asyncio
async def test_extract_policy_force_refresh(
    policy_crawler_service,
    mock_discovery_service,
    mock_content_extractor,
    mock_storage_repository
):
    """
    Test policy extraction with force_refresh=True, bypassing DB check.
    """
    mock_storage_repository.get_existing_policy.return_value = MOCK_POLICY_CONTENT_OBJ # Existing policy in DB
    mock_discovery_service.discover_policy_link.return_value = MOCK_POLICY_URL_DISCOVERY
    mock_content_extractor.extract_content.return_value = MOCK_HTML_CONTENT
    mock_storage_repository.save_policy.return_value = None
    mock_content_processor = AsyncMock(spec=ContentProcessor) # Mock this locally to avoid fixture conflict
    mock_content_processor.process_content.return_value = MOCK_POLICY_CONTENT_OBJ
    policy_crawler_service.content_processor = mock_content_processor # Assign mock to service

    result = await policy_crawler_service.extract_policy(MOCK_WEB_URL, force_refresh=True)

    mock_storage_repository.get_existing_policy.assert_called_once_with(MOCK_ROOT_URL) # Still called, but ignored
    mock_discovery_service.discover_policy_link.assert_called_once_with(MOCK_ROOT_URL)
    mock_content_extractor.extract_content.assert_called_once_with(MOCK_POLICY_URL_DISCOVERY)
    mock_content_processor.process_content.assert_called_once()
    mock_storage_repository.save_policy.assert_called_once()

    assert result == MOCK_POLICY_CONTENT_OBJ

@pytest.mark.asyncio
async def test_extract_policy_existing_policy_cache_hit(
    policy_crawler_service,
    mock_discovery_service,
    mock_content_extractor,
    mock_search_provider,
    mock_content_processor,
    mock_storage_repository
):
    """
    Test policy extraction when policy already exists in DB and force_refresh is False.
    """
    mock_storage_repository.get_existing_policy.return_value = MOCK_POLICY_CONTENT_OBJ

    result = await policy_crawler_service.extract_policy(MOCK_WEB_URL, force_refresh=False)

    mock_storage_repository.get_existing_policy.assert_called_once_with(MOCK_ROOT_URL)
    mock_discovery_service.discover_policy_link.assert_not_called() # Should be skipped
    mock_search_provider.search_policy.assert_not_called() # Should be skipped
    mock_content_extractor.extract_content.assert_not_called() # Should be skipped
    mock_content_processor.process_content.assert_not_called() # Should be skipped
    mock_storage_repository.save_policy.assert_not_called() # Should be skipped

    assert result == MOCK_POLICY_CONTENT_OBJ
